#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
main = root / "apps/orcsdr-tab5/ui/main.cpp"

text = main.read_text()
old = '''  /*
   * Fewer, larger URBs → fewer demod wakeups, longer continuous audio runs.
   * 3 × 32 KiB is the measured continuous-listen profile from Tab5.
   */
  cfg.transfer_bytes = 32768;
  cfg.transfer_count = 3;
'''
new = '''  /*
   * Keep enough USB buffering for 960 kS/s while preserving internal DMA RAM
   * for I2S, display/UI and ESP-Hosted.  The previous 3 x 32 KiB profile
   * consumed too much DMA-capable internal memory on Tab5.
   */
  cfg.transfer_bytes = 16384;
  cfg.transfer_count = 2;
'''

if new in text:
    print("already patched: apps/orcsdr-tab5/ui/main.cpp")
elif old in text:
    main.write_text(text.replace(old, new, 1))
    print("patched: apps/orcsdr-tab5/ui/main.cpp")
else:
    raise SystemExit("RTL transfer profile marker not found")

print("RTL DMA relief profile applied: 2 x 16 KiB")
