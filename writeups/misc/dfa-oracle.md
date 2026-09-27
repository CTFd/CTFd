<!-- nctf-meta category="misc" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# dfa-oracle

Find the single string accepted by a deterministic finite automaton.

## Technique

`automaton.json` is a DFA whose language is a singleton. Internally it is a
linear chain of states spelling the flag: the correct symbol at each step
advances along the chain, and every other symbol falls into one non-accepting
trap state that only loops to itself. The state ids are randomized and the
transition list is shuffled, so the chain is not readable by eye.

## Steps

1. Load the transition table into a `(state, symbol) -> next_state` map.
2. Breadth-first search from `start`, tracking the symbols consumed.
3. The first accepting state reached yields the accepted string — the flag.

Run `python3 solution/solve.py` (pure standard library).

## Flag

`NCTF{…}`
