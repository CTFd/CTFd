<!-- nctf-meta category="osint" difficulty="medium" points="300" author="dagbanjaphet" stub="0" -->

# exif-triangulation

**Category:** osint · **Difficulty:** medium
**Flag:** `NCTF{…}`

## Summary

Four JPEGs each store, in EXIF, the photographer's own GPS position and the GPS
coordinates of the target they observed (`GPSDestLatitude`/`GPSDestLongitude`).
Three agree on one point; the majority coordinate is the flag.

## Technique

EXIF GPS analysis, specifically the often-ignored GPS _Destination_ tags, plus a
majority vote to discard the misattributed (decoy) observation.

## Step by step

1. Parse the EXIF of each `photo_*.jpg`. Read the GPS IFD (tag `0x8825`).
2. Beyond the watcher position, read `GPSDestLatitude` (0x14) /
   `GPSDestLongitude` (0x16) and their refs (0x13 / 0x15). Convert the DMS
   rationals to decimal degrees.
3. `photo_north`, `photo_east`, `photo_west` all point to
   `6.13042 N, 1.22295 E`. `photo_south` points elsewhere (decoy).
4. Take the majority coordinate, format each value to 5 decimals with the dot
   replaced by `p`: flag = `NCTF{…}`.

`solution/solve.py` reads EXIF with a small pure-stdlib TIFF parser (no Pillow /
piexif needed to solve).

## Flag

`NCTF{…}`
