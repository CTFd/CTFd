<!-- nctf-meta category="misc" difficulty="" points="100" author="dagbanjaphet" stub="0" -->

# json-sift

Filter a large JSON array on a two-part predicate, order the survivors, and
read off a per-record payload character.

## Technique

The flag characters are spread across the 5000 records. Exactly the records
with `tag == "delta"` **and** `active == true` carry a real flag character in
`ch`. Records that match only one half of the predicate are decoys, and the
generator guarantees no noise record ever matches both halves. Sorting the real
records by `seq` recovers the intended order.

## Steps

1. Parse `telemetry.json`.
2. Keep records where `tag == "delta"` and `active == true`.
3. Sort them by `seq` ascending.
4. Concatenate each record's `ch`.

```sh
jq -r '[.[] | select(.tag == "delta" and .active == true)]
        | sort_by(.seq) | map(.ch) | join("")' telemetry.json
```

Run `solution/solve.sh` (requires `jq`) to print the flag.

## Flag

`NCTF{…}`
