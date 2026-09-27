<!-- nctf-meta category="forensics" difficulty="medium" points="400" author="ctf-team" stub="0" -->

# Evasion Timeline

**Category:** forensics / DFIR · **Difficulty:** medium(-hard)
**Challenge ID:** `forensics-evasion-timeline`
**Flag:** `NCTF{…}` (static)
**Technique:** MITRE ATT&CK **T1134.004 — Access Token Manipulation: Parent
Process ID (PPID) Spoofing** (tactic: Defense Evasion)

## Artifact

`sysmon.jsonl` — 2,795 newline-delimited Sysmon "Operational" events exported
from a Windows 11 finance workstation over a ~35-minute window: the boot chain,
service host tree, an interactive user session (Chrome/Edge renderers, Outlook,
Teams, VS Code), updaters, scheduled/background tasks, and the usual image-load,
DNS, network, file and registry churn. `TRIAGE_BRIEF.md` sets the IR scene and
lists the Sysmon field meanings; it deliberately does **not** name the technique.

## The evasion, and why it is detectable

An attacker created a malicious process with a **forged parent** (Windows
`PROC_THREAD_ATTRIBUTE_PARENT_PROCESS` / `UpdateProcThreadAttribute`). Sysmon
faithfully records the _spoofed_ `ParentProcessId` / `ParentProcessGuid` it was
handed, so the process tree _looks_ clean — the malicious PowerShell appears to
descend from a trusted `wermgr.exe` (PID **6284**), a normal Windows Error
Reporting host.

The lie is only visible on the **timeline**:

| event                                                                    | ProcessGuid      | UtcTime  |
| ------------------------------------------------------------------------ | ---------------- | -------- |
| `wermgr.exe` **created** (PID 6284)                                      | `{715573D9-...}` | 08:33:07 |
| `wermgr.exe` **terminated** (EventID 5)                                  | `{715573D9-...}` | 08:33:12 |
| malicious `powershell.exe` created, **claiming parent `{715573D9-...}`** | `{30207CEC-...}` | 08:33:40 |

The claimed parent had already **terminated 28 seconds earlier**. A dead process
cannot spawn a child, so the recorded ancestry is impossible — this is the
signature of PPID spoofing. It is the **only** such broken parent/child edge in
the entire capture.

## Intended solve path

1. Index every Process-Create (EventID 1) by `ProcessGuid`; record the earliest
   Process-Terminate (EventID 5) time per `ProcessGuid`.
2. For each child whose `ParentProcessGuid` was actually created in this capture,
   assert the parent was **alive** at the child's birth:
   `parent.create <= child.create <= parent.terminate` (or parent never
   terminated). Root processes whose parent is outside the capture are ignored.
3. Exactly one event fails: the malicious `powershell.exe`
   (`-nop -w hidden -ep bypass -enc <base64>`).
4. Decode its `-EncodedCommand` (base64 of UTF-16LE — standard PowerShell
   `-EncodedCommand`). The decoded one-liner embeds the flag:
   `$p=6284;$c='NCTF{…}';...`
   The trailing `6284` echoes the spoofed `ParentProcessId`, confirming the
   IOC ⇄ flag correspondence.

Run it:

```
python3 solve.py ../sysmon.jsonl
```

Verified output:

```
[*] 318 process-create events, 296 distinct terminations
[*] impossible-ancestry events found: 1
[+] Defense-evasion IOC (forged parent / PPID spoof):
      malicious Image  : ...\powershell.exe
      claimed parent   : PID 6284 (...\wermgr.exe) guid {715573D9-...}
      parent TERMINATED: 2024-11-05 08:33:12  (28s before the child)
[*] decoded -EncodedCommand:
      $p=6284;$c='NCTF{…}';...
[+] FLAG: NCTF{…}
```

## The decoy (one, refutable — not self-labelled)

A second process — a hidden PowerShell downloader launched by `explorer.exe` —
also carries a flag-shaped token in its encoded command:
`NCTF{…}`. So a solver who simply base64-decodes
**every** `-EncodedCommand` and greps for `NCTF{` gets **two** candidates and no
way to choose. The decoy is refutable purely from the evidence: its parent
(`explorer.exe`, PID 4012) is a long-lived, still-alive process, so its ancestry
is sound — it did **not** evade detection. Only the process with the impossible
parentage carries the real flag. There is no "fake"/"not-the-flag" label; the
decoy looks like a genuine malicious downloader and must be discarded by
reasoning, not by reading a hint.

## Why this resists a one-shot LLM answer

- **Not a name/path signature.** The malicious image is a legitimate
  `powershell.exe` under `System32`, its parent is a legitimate `wermgr.exe`, and
  its encoded command looks like the several _benign_ admin `-EncodedCommand`
  invocations elsewhere in the log. Pattern-matching "suspicious process" gets
  you nowhere.
- **The tell is a relationship across two events at different times**, buried in
  ~2,800 events — a Process-Terminate for a GUID, then a later Process-Create
  claiming that GUID as parent. You must build the create/terminate index and
  compare timestamps, not scan lines.
- **Two flag-shaped strings.** A model that shortcuts to "decode all encoded
  PowerShell and grab the NCTF" will likely surface the decoy. Choosing
  correctly _requires_ the timeline correlation.

## Reproducing the log

`../gen.py` deterministically rebuilds `sysmon.jsonl` (fixed RNG seed):

```
cd .. && python3 gen.py     # writes ./sysmon.jsonl
```

`gen.py` is intentionally excluded from the player bundle (`files:` in
`challenge.yml` ships only `sysmon.jsonl` and `TRIAGE_BRIEF.md`). The flag, the
spoofed PID, and the anomaly construction are defined at the top of that script.
The log data is original synthetic telemetry generated here — no third-party
sample corpus is downloaded, used, or shipped.
