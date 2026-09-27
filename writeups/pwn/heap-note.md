<!-- nctf-meta category="pwn" difficulty="medium" points="350" author="dagbanjaphet" stub="0" -->

# heap-note

**Category:** pwn · **Difficulty:** medium
**libc:** glibc 2.31 (Ubuntu 20.04, `2.31-0ubuntu9.18`), pinned and shipped.
**Binary:** `-no-pie`, NX, no canary. tcache present, **no safe-linking** (that
arrived in 2.32).

## The service

A 16-slot note manager: `alloc(idx,size)`, `free(idx)`, `edit(idx)`,
`view(idx)`. Two deliberate bugs, both use-after-free:

- `free()` frees the chunk but **does not clear `notes[idx]`**.
- `edit()` and `view()` operate on `notes[idx]` with **no live/freed check**.

So a freed slot can still be read (`view` → leak) and written (`edit` →
edit-after-free, i.e. tcache metadata corruption).

The flag is **not in the binary**. `win()` prints `getenv("FLAG")`, is called
by no menu path, and the service injects the per-team flag into the environment
at runtime (`entrypoint.sh` ← `flag.py` ← `TEAM_SECRET`). You must actually
redirect execution into `win()`; the service emits the flag only as a side
effect of that.

## Solve path

### 1. Leak libc (UAF read of an unsorted-bin chunk)

tcache bins only cover request sizes up to 0x408 (chunk 0x410). Allocate a chunk
bigger than that (`0x500`) plus a small **guard** after it (so it isn't merged
into the top chunk), then free the big one. It lands in the **unsorted bin**,
whose lone member has `fd == bk ==` the unsorted-bin list head, which lives at
`&main_arena + 0x60`. `view` the freed slot to read that pointer.

For glibc 2.31/x86-64, `&main_arena + 0x60 == __malloc_hook + 0x70`
(`main_arena == __malloc_hook + 0x10`). So:

```
libc_base = leak - (libc.sym['__malloc_hook'] + 0x70)
```

(You can also derive the offset directly from the shipped `libc.so.6`; the
solver does exactly the symbol arithmetic above, no magic constants.)

### 2. tcache poisoning (edit-after-free) → `__free_hook`

Because 2.31 stores tcache `fd` un-mangled, poisoning is a raw pointer write.
Note the tcache **count gate**: `__libc_malloc` only serves from tcache while
`counts[idx] > 0`, so you need **two** chunks in the bin, not one, to get two
allocations back out.

```
alloc(2,0x18); alloc(3,0x18)      # two 0x20 chunks
free(2); free(3)                  # tcache[0x20]: head=3 -> 2   (count=2)
edit(3, p64(&__free_hook))        # edit-after-free: overwrite the head's fd
alloc(4,0x18)                     # returns chunk 3; head becomes &__free_hook
alloc(5,0x18)                     # returns a chunk *at* &__free_hook
edit(5, p64(&win))                # __free_hook = win
```

No alignment check exists on the tcache fetch path in 2.31, and `&__free_hook`
sits in a zeroed region so the fixed-size `edit` write is harmless collateral.

### 3. Trigger

`__libc_free` reads `__free_hook` before it touches the chunk, so **any** free
now calls `win()`:

```
free(1)   # __free_hook(ptr) == win() -> prints NCTF{…}
```

## Running the solver

```
# Local (spawns handout/chall under the shipped ld + libc; no patchelf needed):
FLAG='NCTF{…}' python3 solve.py

# Remote:
python3 solve.py <host> 9022
```

To run the handout binary by hand offline, invoke the shipped loader directly:

```
cd handout
./ld-2.31.so ./chall          # rpath is $ORIGIN, so it finds ./libc.so.6
# or: patchelf --set-interpreter ./ld-2.31.so --set-rpath . chall && ./chall
```

## Verification performed

This exploit was run end-to-end in the authoring environment against the exact
shipped `handout/chall` + `handout/libc.so.6` + `handout/ld-2.31.so`
(glibc 2.31-0ubuntu9.18) and reliably reaches `win()` and prints the FLAG. The
measured unsorted-bin-head offset matched `__malloc_hook + 0x70` and the
`R_X86_64_GLOB_DAT` for `__free_hook` confirmed the `free()` indirection, both
checked live with gdb.

The Docker image itself was **not** built here (no Docker daemon in the
authoring sandbox). The image simply ships this same, verified binary and
patchelf-binds it to the same libc/ld, so the served behaviour equals the
locally verified behaviour; a build + `solve.py <host> 9022` smoke test is the
recommended pre-event check.

## Honest note on LLM assistance

A frontier model recognises this instantly as "UAF → tcache poison →
`__free_hook` → win" and can draft most of the pwntools. Where it still trips,
and why this stays worth a medium:

- **The count gate.** The single most common wrong first attempt is one free +
  one poisoned fetch; that fails silently because `counts[idx]` hits 0. You must
  free twice.
- **Pinned-libc arithmetic.** The leak is the unsorted-bin head, not a symbol.
  Getting `libc_base` right means knowing it is `__malloc_hook + 0x70` for this
  build (or deriving it), and the exploit is worthless against any other libc —
  the offsets are specific to `2.31-0ubuntu9.18`, which is why it is shipped.
- **Raw-byte I/O.** Addresses contain NULs and newlines, so `content` must be a
  fixed-length `read(2)`, and the service must be a byte-transparent socket (no
  pty). A model that reflexively uses `sendline`/`fgets` framing corrupts the
  poison.
- **Server-side oracle.** There is nothing to grep. The only way to produce the
  flag is to actually corrupt the allocator and land in `win()` on the live
  instance, so an offline agent cannot brute a flag out of the artifact.

The decoy (`secret_backdoor` → `NCTF{…}`)
is refuted in seconds: it is unreferenced and reads no environment, and event
rules say a constant in a shipped file is never the real flag.
