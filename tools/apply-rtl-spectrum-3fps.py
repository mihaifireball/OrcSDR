#!/usr/bin/env python3
from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'apps/orcsdr-tab5/ui/main.cpp'
s = p.read_text()
old = 'constexpr uint32_t kRtlSpectrumIntervalMs = 200;\nconstexpr uint32_t kRtlSpectrumStressedIntervalMs = 350;'
new = 'constexpr uint32_t kRtlSpectrumIntervalMs = 333;\nconstexpr uint32_t kRtlSpectrumStressedIntervalMs = 500;'
if new in s:
    print('already patched: RTL spectrum ~3 FPS')
    raise SystemExit(0)
if s.count(old) != 1:
    raise SystemExit('expected 5 FPS spectrum marker exactly once; file unchanged')
p.write_text(s.replace(old, new, 1))
print('patched: RTL spectrum interval 200->333 ms, stressed 350->500 ms')
