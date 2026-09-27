<!-- nctf-meta category="hardware" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# vcd-fsm

**Flag:** `NCTF{…}`

## TL;DR

`trace.vcd` is a Value Change Dump of a Moore state machine. Sample the `dout`
bus on each rising edge of `clk`; the byte sequence is the flag.

## VCD format refresher

- The header lists signals with `$var <type> <width> <id> <name> [range] $end`.
  Here: `clk` → `!`, `state` → `"`, `dout` → `#`, `noise` → `$`.
- After `$enddefinitions`, `#<time>` lines mark simulation times and are
  followed by value changes: scalars as `1!` / `0!`, vectors as `b0100 #`.
- A signal keeps its last value until it changes again.

## Solve steps

1. Parse the `$var` map and the ordered list of `(time, id, value)` changes.
2. Replay the changes in time order, keeping the current value of every signal.
   Settle all changes that share a timestamp before sampling.
3. On every `clk` rising edge (0→1), read the current `dout` value and convert
   the 8-bit string to a byte.
4. Concatenate → ASCII flag. `noise` changes only on the falling half-cycle, so
   sampling strictly on the rising edge avoids it.

Run the solver:

```
python3 solution/solve.py            # uses ../trace.vcd
python3 solution/solve.py trace.vcd
```

It prints `NCTF{…}`.
