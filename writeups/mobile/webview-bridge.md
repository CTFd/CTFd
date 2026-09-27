<!-- nctf-meta category="mobile" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# webview-bridge

**Category:** mobile · **Difficulty:** medium
**Flag:** `NCTF{…}`

## Summary

A hybrid Android app exposes a `@JavascriptInterface` bridge to its WebView. The
bundled JS calls one bridge method with a fixed token, and the bridge decrypts
an embedded blob keyed by that token. Reading both recovers the flag.

## The technique

Inside the APK:

- `assets/app.js` → `AndroidBridge.getSecret("brg_2f9a_unlock_token")`
- `sources/com/hybrid/shop/JsBridge.java` → base64 `ENC` + the decrypt loop

```
ks[i] = sha256(token || byte(i/32))[i % 32]
flag  = base64_decode(ENC) XOR ks
```

The plaintext flag is never stored.

## Solve

```
$ python3 solve.py hybridshop.apk
bridge token: brg_2f9a_unlock_token
flag: NCTF{…}
```

## Rebuilding

```
python3 src/gen.py    # writes hybridshop.apk with the flag embedded
```
