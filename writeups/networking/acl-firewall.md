<!-- nctf-meta category="networking" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# acl-firewall

**Summary:** Emulate a first-match-wins ACL with implicit default-deny, collect
the allowed flows, sort by `id`, and read their `tag` characters.

## Technique

The policy is an ordered access list. For each flow:

- A rule matches when `src` and `dst` fall inside the rule's CIDRs and the
  protocol and destination port match (`any` is a wildcard).
- The action of the **first** matching rule is applied.
- If nothing matches, the flow is dropped (implicit default-deny).

The ruleset deliberately places a specific `deny tcp/22` above a broad
`allow ... /443` and a broad `deny`, so naive "does any allow rule match" logic
gives the wrong answer.

## Steps

1. Parse `ruleset.json`.
2. Evaluate each flow top-to-bottom, first match wins, else deny.
3. Keep the allowed flows, sort ascending by `id`.
4. Concatenate their `tag` fields.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
