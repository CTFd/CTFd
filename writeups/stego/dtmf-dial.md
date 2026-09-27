<!-- nctf-meta category="stego" difficulty="hard" points="450" author="dagbanjaphet" stub="0" -->

# dtmf-dial

The flag is dialled out as DTMF (telephone touch-tone) digits.

## Technique

Each flag byte is written as three decimal digits (000-255). Every digit is
synthesised as its standard DTMF dual-tone pair (one low-group + one high-group
frequency), separated by short silences.

## Solve

1. Split the WAV into tone bursts by energy (windowed RMS).
2. For each burst, run a Goertzel filter (or FFT) at the four low
   (697/770/852/941 Hz) and four high (1209/1336/1477/1633 Hz) DTMF
   frequencies; the strongest pair identifies the keypad digit.
3. Concatenate the digits, then read them three at a time as ASCII codes.

Run `python solve.py` to print the flag.

## Flag

`NCTF{…}`
