<!-- nctf-meta category="forensics" difficulty="hard" points="500" author="ctf-team" stub="0" -->

# Audio FSK

**Flag:** `NCTF{…}`

## TL;DR

`transmission.wav` is a continuous-phase 2-FSK downlink. The physical layer is
deliberately non-standard, so canned tools fail:

| parameter       | value                                     |
| --------------- | ----------------------------------------- |
| sample rate     | 48000 Hz (from the WAV header)            |
| baud            | **96** (exactly 500 samples/symbol)       |
| mark (bit `1`)  | **1855 Hz**                               |
| space (bit `0`) | **3145 Hz** (space is _higher_ than mark) |
| bit order       | MSB-first                                 |
| framing         | preamble → sync → len → payload → CRC-8   |
| sync word       | `0x9E 0x3A`                               |

There are **no UART start/stop bits** on the primary link — it is a raw
contiguous bitstream framed by a preamble and a custom sync word, with a CRC-8
(poly `0x07`, over `LEN‖PAYLOAD`) trailer.

## Solve path

1. **Confirm it is FSK.** A spectrogram (or a plain FFT of the loud burst) shows
   two dominant tones, ~1855 Hz and ~3145 Hz. These are _not_ Bell-103
   (1270/1070) or Bell-202 (1200/2200), so `minimodem` defaults will not work.

2. **Measure the two tones.** Window the energetic burst and take an FFT; the two
   highest peaks are the mark/space frequencies.

3. **Measure the baud.** The preamble is `0xAA` repeated — alternating tones —
   so the shortest transition spacing is one symbol. A run-length estimate lands
   near 480–500 samples; refine it by searching for the samples-per-symbol that
   yields a CRC-valid frame. It locks at 500 samples/symbol → **96 baud**.

4. **Slice and demodulate.** Cut the burst into 500-sample symbols, and for each
   symbol compare the Goertzel power at the two tones (sampling the middle third
   avoids continuous-phase transition smear) to get one raw bit per symbol.

5. **Resolve polarity + alignment.** You do not yet know which tone is `1` nor
   where bytes start. Search the raw bit string for the sync word `0x9E3A`
   (MSB-first) under both polarities. Exactly one polarity produces the sync word
   cleanly right after the alternating preamble — that fixes both unknowns.

6. **Frame and verify.** After the sync word: read `LEN`, then `LEN` payload
   bytes, then the CRC-8 byte. CRC-8 (poly `0x07`, init `0x00`, no reflection)
   over `LEN‖PAYLOAD` must match. It does, which confirms the framing.

7. **Read the payload:**
   ```
   SIGINT downlink 0x2217 :: frame recovered :: flag=NCTF{…} :: end of transmission
   ```

Run the reference solver:

```
python3 solve.py ../transmission.wav
```

It auto-detects the tones, refines the baud via CRC, resolves polarity/alignment
via the sync word, and prints the flag. (Requires only `numpy` + stdlib; takes
~10 s because of the CRC-driven baud/phase search.)

## The decoy

Later in the recording, at ~1/13th the amplitude, there is a **textbook Bell-202
link**: 1200 baud, mark 1200 Hz / space 2200 Hz, standard UART 8N1, LSB-first. A
solver who runs `minimodem` (or any default-settings FSK decoder) against the
file can lock onto it and recover:

```
NCTF{…}
```

It is refutable in minutes: it uses _exactly_ the standard parameters the brief
says the primary link avoids, and it has none of the preamble/sync/CRC framing
the brief describes. The real payload is CRC-verified; the decoy is not. The
decoy sits below the burst-detection threshold, so the reference solver's tone
and baud estimates never see it.

## What an LLM does well / badly here

- **Well:** recognising the spectrogram shows 2-FSK, writing a Goertzel/FFT
  demodulator, and computing a CRC-8 once told the polynomial. These are
  standard and a model produces them quickly.
- **Badly / where it stalls:** the challenge resists a single prompt. A first
  attempt almost always assumes Bell-202 + UART 8N1 (and may proudly return the
  **decoy** flag). Getting the real flag requires _measuring_ the non-standard
  tones and baud from the signal, realising there are **no start/stop bits**,
  discovering the sync word `0x9E3A`, and resolving the tone→bit polarity — an
  iterative, evidence-driven loop, not a recall task. The continuous-phase edges
  also punish naive full-symbol integration, nudging you toward mid-symbol
  sampling. The CRC is the honest oracle that tells you when you are actually
  right, so guessing does not pay.
