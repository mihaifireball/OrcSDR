#!/usr/bin/env python3
from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'apps/orcsdr-tab5/ui/main.cpp'
s = p.read_text()
old = 'constexpr uint32_t kRtlSpectrumIntervalMs = 100;\nconstexpr uint32_t kRtlSpectrumStressedIntervalMs = 220;'
new = 'constexpr uint32_t kRtlSpectrumIntervalMs = 200;\nconstexpr uint32_t kRtlSpectrumStressedIntervalMs = 350;'
if new in s:
    print('already patched: RTL spectrum 5 FPS')
    raise SystemExit(0)
if s.count(old) != 1:
    raise SystemExit('expected spectrum interval marker exactly once; file unchanged')
p.write_text(s.replace(old, new, 1))
print('patched: RTL spectrum interval 100->200 ms, stressed 220->350 ms')
