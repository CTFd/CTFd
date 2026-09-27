<!-- nctf-meta category="misc" difficulty="easy" points="100" author="ctf-authoring" stub="0" -->

# git-archaeology

**Category:** misc (git forensics) · **Difficulty:** easy
**Flag:** `NCTF{…}`

## Scenario

Players download `logparse-cli.tar.gz`, which contains a small project **and its
`.git` directory**. A production `upload_token` was once committed to
`config.ini` and then "removed." The trick: it was removed with
`git reset --hard`, which only moves the branch pointer. Running `git log` shows
a perfectly clean history — the secret commit is no longer reachable from `main`
— but the commit object (and its blob) still live in `.git/objects`, and the
reflog still points at them.

## Intended solve

Extract the tarball and look around:

```bash
tar xzf logparse-cli.tar.gz && cd logparse-cli
git log --oneline          # clean history, no secret
git log -p --all           # traverses refs only -> only shows the DECOY token
```

`git log --all` walks refs, not the reflog, so it will **not** reach the dropped
commit. It _will_ surface the decoy in `NOTES.txt`
(`NCTF{…}`), which is clearly labelled as a fake
placeholder. Ignore it.

Now do the actual archaeology. Any of these finds the dangling commit:

```bash
# (a) the reflog remembers the reset
git reflog
#   ... 70c39b0 HEAD@{3}: commit: wire up analytics upload (temp: real token, will scrub)

# (b) fsck lists dangling objects directly
git fsck --lost-found
#   dangling commit 70c39b029c1a62d4edd9a58ffbebb8af905c8067
```

Read the scrubbed config out of that commit:

```bash
git show 70c39b0:config.ini
# upload_token = NCTF{…}
```

Or `git cat-file -p 70c39b0` → tree → blob if you prefer plumbing. Done.

An automated version is in [`solve.sh`](solve.sh):

```bash
./solve.sh ../logparse-cli.tar.gz
# NCTF{…}
```

## The decoy

`NOTES.txt` contains `NCTF{…}` in a bullet that
literally says "this is a fake sample value." It is reachable from normal
history, so a player who only greps `git log -p` finds it first. It is refutable
in seconds from the note's own text and from the fact that it is _not_ the
scrubbed `upload_token` the description asks for. Exactly one decoy, no attempt
cost.

## Rebuilding

`build_repo.sh` (in the challenge root) deterministically reconstructs the repo
and tarball. It fixes author/committer identity and dates, asserts the secret
commit is unreachable-but-present, and crucially never runs `git gc`/`git prune`
(which would destroy the dangling objects). Re-run it to regenerate the artifact.

## Honesty note — how an LLM does here

This is a well-known git-forensics motif, so a capable LLM/agent will very likely
one-shot it _if it can run git_ against the extracted repo: `git reflog` +
`git show` is the canonical move and is all over training data. The mild
friction is (1) recognising that `git log`/`git log --all` is deliberately clean
and that the reflog/`fsck` is required, and (2) not stopping at the decoy token.
It stays an honest **easy**: no obfuscation, the artifact is the challenge, and
the value lives only in a dangling object rather than in tracked history. It
rewards knowing that `reset --hard` doesn't delete anything, not guesswork.
