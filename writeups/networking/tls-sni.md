<!-- nctf-meta category="networking" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# tls-sni

**Summary:** Parse the TLS ClientHello structure, read the SNI hostname, and
hex-decode its labels into the flag.

## Technique

No cryptography — pure structure parsing:

```
record:    type(1)=0x16 | version(2) | length(2)
handshake: type(1)=0x01 | length(3)
body:      client_version(2) | random(32) | session_id(len+data)
           | cipher_suites(len2+data) | compression(len1+data)
           | extensions(len2 + [type(2) len(2) data]...)
```

The **server_name** extension (type `0x0000`) holds the SNI hostname. Its body
is `list_len(2) | name_type(1=host_name) | name_len(2) | hostname`.

The hostname is dot-separated **hex** labels followed by the fixed suffix
`.v.nctf`. Drop the suffix, join the hex labels, and hex-decode.

Decoys are planted in the client `random` field and in an ALPN entry, so a
`grep NCTF{…}

```

```
