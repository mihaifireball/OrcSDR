#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = root / "apps/orcsdr-tab5/ui/main.cpp"
text = p.read_text()

old = '''      while (dsp_elapsed_us > previous_max &&
             !rtl_dsp_block_us_max.compare_exchange_weak(
                 previous_max, dsp_elapsed_us, std::memory_order_relaxed)) {
      }
      break;
'''
new = '''      while (dsp_elapsed_us > previous_max &&
             !rtl_dsp_block_us_max.compare_exchange_weak(
                 previous_max, dsp_elapsed_us, std::memory_order_relaxed)) {
      }
      // DSP, audio and UI share core1.  A zero-delay yield after every
      // completed IQ block lets equal/higher-priority UI work run without
      // adding a full RTOS tick of latency to the SDR stream.
      taskYIELD();
      break;
'''

if new in text:
    print("already patched: RTL DSP/UI yield")
    raise SystemExit(0)

count = text.count(old)
if count != 1:
    raise SystemExit(f"marker count for DSP/UI yield is {count}, expected 1; source left unchanged")

p.write_text(text.replace(old, new, 1))
print("patched: RTL DSP/UI yield after each completed IQ block")
