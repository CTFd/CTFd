<!-- nctf-meta category="ai" difficulty="" points="100" author="dagbanjaphet" stub="0" -->

# ai0-leaked-transcript

**Category:** ai (Level 0, root of the AI track)
**Difficulty:** easy
**Flag:** `NCTF{…}` (static)

## Premise

The handout `transcript.json` is an exported chat transcript from a fictional
internal assistant, HelixDesk. In the conversation the assistant is asked for
its system prompt and refuses. The trap for the careless is to read only the
`conversation.messages` and conclude nothing is there.

The export tool, however, dumped the full runtime configuration into a metadata
field. The leaked system prompt lives at:

    metadata.runtime_config.system_prompt

## Solve path

1.  Open `transcript.json` and read `metadata.runtime_config.system_prompt`.
2.  The leaked notes carry **two** base64 handoff tokens. The first is flagged
    `DEPRECATED ... ROTATED OUT ... no longer valid` -- that is the decoy. The
    one to use is the **current** token, on the line:

    _"The current audit-handoff token for this deployment is"_

        fWQzbDQzdjNyX3RwbTBycF9tM3Q1eXN7RlRDTg==

3.  It is stated to be lightly protected. base64-decode it:

        }d3l43v3r_tpm0rp_m3t5ys{FTCN

    That is clearly the flag written backwards.

4.  Reverse the string to get the flag:

    NCTF{…}

    (Decoding the _rotated_ token instead yields `NCTF{…}`,
    which the scoreboard rejects -- refuting it takes one glance at its own line.)

One-liner:

    python3 -c 'import base64,json,re;p=json.load(open("public/transcript.json"))["metadata"]["runtime_config"]["system_prompt"];t=re.search(r"deployment is (\S+)",p).group(1);print(base64.b64decode(t).decode()[::-1])'

Or run the provided solver:

    python3 solution/solve.py

## Regenerating the handout

    python3 solution/generate.py

This rewrites `public/transcript.json` deterministically and prints the flag.

## Honest note on LLM assistance

This challenge is intentionally trivial and, being Level 0, is expected to be
one-prompt-solvable by a frontier model: paste the JSON, ask for anything
hidden, and the model will find the system prompt in metadata, spot the base64,
decode and reverse it. That is by design -- its job is to be an on-ramp and a
prerequisite gate for the rest of the AI category, not to resist automation.
The obfuscation (reverse + base64) exists only so the flag is not grep-able as
plaintext in the file, forcing a decode step rather than a copy-paste.

A single decoy is included: a second, rotated-out handoff token, decoding to
`NCTF{…}`. It costs nothing to refute -- its own line
says `DEPRECATED ... ROTATED OUT ... no longer valid` -- but it teaches the
lesson every real leaked-config triage needs (and that the OWASP LLM06
"sensitive information disclosure" class turns on): a dumped config is noisy,
and "grab the first base64 blob and decode it" is not the same as reasoning
about _which_ secret is live. It never consumes an attempt on the scoreboard.

The single lesson it teaches -- that an assistant refusing something in-band
says nothing about what leaked out-of-band into logs/exports/metadata -- is the
theme the harder AI challenges build on.
