<!-- nctf-meta category="supplychain" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# layered-image-leak

A secret deleted in a later image layer still lives in the earlier layer that
added it.

## Vulnerability

The `docker save` tar keeps every layer. The secret `app/config/secret.env` is
added in the first layer, then a later layer "removes" it with an overlayfs
whiteout (`app/config/.wh.secret.env`). The whiteout only hides the file in the
flattened filesystem; the bytes remain in the earlier layer blob.

## Solve

1. Open `image.tar`, read `manifest.json` to get the ordered `Layers`.
2. Walk each `layer.tar`. Note the whiteout `.wh.secret.env` in the top layer.
3. Read `app/config/secret.env` from the earlier layer that still contains it.
4. Its `DEPLOY_KEY=` value is base64(flag). Decode it.

Run:

```
python3 solution/solve.py
```

## Flag

```
NCTF{…}
```
