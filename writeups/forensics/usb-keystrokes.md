<!-- nctf-meta category="forensics" difficulty="easy" points="150" author="ctf-team" stub="0" -->

# USB Keystrokes

**Category:** forensics · **Difficulty:** easy
**Flag:** `NCTF{…}`

## What you get

`capture.pcap` — a raw Linux **usbmon** capture (link type
`LINKTYPE_USB_LINUX_MMAPPED`, DLT 220). Wireshark and tshark both parse it as
"USB URB" packets.

## The idea

A USB HID boot keyboard reports key state as an 8-byte packet on its
interrupt-IN endpoint:

```
byte 0 : modifier bitmap (bit1/bit5 = left/right Shift, etc.)
byte 1 : reserved (0x00)
byte 2 : keycode #1  (USB HID Usage Table, Keyboard/Keypad page 0x07)
byte 3..7 : keycodes #2..#6 (rollover)
```

Each key press produces a report with a usage code in byte 2, followed by a
"release" report of all zeros when the key comes back up. Decoding is:
map the usage code to its character via the HID usage table, and if a Shift
bit is set in byte 0, use the shifted character (so `b`→`B`, `-`→`_`, `2`→`@`…).

## The two traps

1. **Two devices are on the bus.** Besides the keyboard (device address 3,
   8-byte reports) there is a **mouse** (device address 5, 4-byte reports)
   producing motion noise the whole time. If you dump _every_ interrupt
   `usb.capdata` and decode it, the mouse bytes corrupt the text. This is the
   intended decoy — and it is instantly refutable: the mouse reports are
   4 bytes, not 8, and sit on a different device address. Filter to the device
   whose reports are 8 bytes long (address 3).

2. **Submit vs complete + releases.** usbmon shows both `S` (submit) and `C`
   (complete) events. Only the `C` interrupt-IN events carry the report data;
   the `S` events have zero captured bytes. And the all-zero release reports
   must be dropped or you get nothing useful from them.

## Solve with Wireshark / tshark

```
tshark -r capture.pcap \
  -Y 'usb.device_address==3 && usb.transfer_type==0x01 && usb.capdata' \
  -T fields -e usb.capdata
```

Then map each 8-byte report's 3rd byte through the HID usage table, applying
Shift from the 1st byte. Reading them in order and skipping the `00` releases
spells the passphrase.

## Solve with the provided script

```
python3 solve.py capture.pcap
```

It parses the usbmon header directly (no Wireshark needed), auto-detects the
keyboard as the device with 8-byte reports, decodes with Shift handling, and
prints:

```
passphrase: Bl4ck_H4t_USB_2026
flag:       NCTF{…}
```

## Regenerating the artifact

`../gen_pcap.py` builds `capture.pcap` deterministically (`random.seed`), so the
bytes are reproducible. The HID reports come from the real USB HID usage table
and the standard boot-keyboard layout, serialised through the genuine 64-byte
usbmon header struct — no hand-faked bytes.

## Honest note on LLM difficulty

A frontier LLM knows the USB HID usage table and the usbmon format cold, so the
"decode keystrokes from a USB pcap" _skeleton_ is nearly one-prompt solvable.
This challenge is kept from being trivial by three concrete, evidence-driven
snags rather than by obscurity:

- The **mouse decoy** on a second device address means a blind "decode all
  interrupt capdata" prompt yields garbage; the model has to notice the two
  devices and filter by report length / address.
- **Shift handling** is required for `B`, `H`, `U`, `S` and the underscores
  (`_` = Shift+`-`). A solve that ignores the modifier byte returns
  `bl4ck-h4t-usb-2026`, which is wrong — a plausible near-miss, not the flag.
- The **submit/release** noise must be filtered.

None of these need telepathy — every one is visible in the capture — but they
do require reading the evidence instead of pattern-matching a template, which
is what keeps it an honest _easy_ rather than a freebie.
