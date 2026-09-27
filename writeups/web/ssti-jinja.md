<!-- nctf-meta category="web" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# ssti-jinja

**Summary:** The `name` is concatenated into the Jinja template source before
rendering, so a `{{ config }}` payload is evaluated and leaks the `config`
global. The flag is sealed with a key derived from that rendered output, so you
must actually evaluate the SSTI -- there is no constant key to call.

## Vulnerability

`render_card` builds `env.from_string("Dear " + name + ", welcome to Lome!")`.
User input becomes part of the template source, i.e. server-side template
injection. The render environment exposes a `config` global (a leakable,
framework-style config object).

The flag ships sealed in `_SEALED`. It is unsealed by XORing with
`keystream(sha256(<rendered leak>))`, where `<rendered leak>` is the exact card
string produced by rendering the intended payload. The key is therefore **not**
a constant in the handout: only evaluating `{{ config }}` against the shipped
template reproduces it. Rendering any other name derives a wrong key and the
unseal fails.

## Steps

1. Recognise the name is placed in the template source, not passed as data.
2. Send `name = "{{ config }}"`; the card renders to
   `Dear Config(DEBUG=..., KIOSK=..., SIGNING_SALT=...), welcome to Lome!`.
3. Use that exact rendered string as the seal key: XOR `_SEALED` with
   `keystream(sha256(rendered))` (helper `unseal` in `app.py`) to recover the
   flag.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
