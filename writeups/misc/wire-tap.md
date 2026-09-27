<!-- nctf-meta category="misc" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# wire-tap

Recover a protobuf message's structure from raw wire bytes and un-XOR the flag.

## Technique

`message.bin` is a Protocol Buffers message with no accompanying `.proto`. The
wire format is self-delimiting: each field is a varint key encoding
`field_number << 3 | wire_type`, followed by the value (a varint for wire type
0, a length-prefixed blob for wire type 2). The recoverable schema is:

- field 1 (varint): version
- field 2 (varint): a single-byte XOR key
- field 3 (varint, repeated): decoy timestamps
- field 4 (length-delimited): nested message
  - field 1 (varint): flag length
  - field 2 (length-delimited): flag bytes XORed with the key

Storing the flag XORed keeps it out of `strings` output.

## Steps

1. Parse the outer message's varint keys and values.
2. Read field 2 as the XOR key byte.
3. Descend into field 4, parse it, and take its field 2 byte string.
4. XOR each byte with the key.

Run `python3 solution/solve.py` (pure standard library), or inspect with
`protoc --decode_raw < message.bin`.

## Flag

`NCTF{…}`
