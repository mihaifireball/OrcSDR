#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
hpp = root / "apps/orcsdr-tab5/ui/home_dashboard.hpp"
cpp = root / "apps/orcsdr-tab5/ui/home_dashboard.cpp"
main = root / "apps/orcsdr-tab5/ui/main.cpp"


def replace_once(path: Path, old: str, new: str):
    text = path.read_text()
    if new in text:
        print(f"already patched: {path.relative_to(root)}")
        return
    if old not in text:
        raise SystemExit(f"marker not found in {path.relative_to(root)}")
    path.write_text(text.replace(old, new, 1))
    print(f"patched: {path.relative_to(root)}")

replace_once(
    hpp,
    '  char wifi_ip[16]{};\n  char mode[12]{};\n',
    '  char wifi_ip[16]{};\n  char receiver[16]{};\n  char mode[12]{};\n',
)

replace_once(
    cpp,
    'void draw_footer_receiver() {\n  M5.Display.fillRect(30, 660, 136, 36, kPanel);\n  footer_text("RTL-SDR v4", 98, current.driver_ready ? kGreen : TFT_ORANGE);\n}\n',
    'void draw_footer_receiver() {\n  M5.Display.fillRect(30, 660, 136, 36, kPanel);\n  footer_text(current.receiver[0] ? current.receiver : "RTL-SDR", 98,\n              current.driver_ready ? kGreen : TFT_ORANGE);\n}\n',
)

replace_once(
    main,
    '  snapshot.driver_ready = demo || device.rtl_ready;\n  snapshot.receiving = demo ||\n',
    '  snapshot.driver_ready = demo || device.rtl_ready;\n  if (demo) {\n    strlcpy(snapshot.receiver, "RTL-SDR V4", sizeof(snapshot.receiver));\n  } else if (rtl_is_blog_v3.load(std::memory_order_acquire)) {\n    strlcpy(snapshot.receiver, "RTL-SDR V3", sizeof(snapshot.receiver));\n  } else if (snapshot.driver_ready) {\n    strlcpy(snapshot.receiver, "RTL-SDR V4", sizeof(snapshot.receiver));\n  } else {\n    strlcpy(snapshot.receiver, "RTL-SDR", sizeof(snapshot.receiver));\n  }\n  snapshot.receiving = demo ||\n',
)

replace_once(
    main,
    '  snapshot.usb_connected = snapshot.vbus_mv >= 4000;\n',
    '  snapshot.usb_connected = snapshot.driver_ready;\n',
)

replace_once(
    main,
    '      snapshot.driver_ready != previous.driver_ready ||\n      snapshot.receiving != previous.receiving ||\n',
    '      snapshot.driver_ready != previous.driver_ready ||\n      strcmp(snapshot.receiver, previous.receiver) != 0 ||\n      snapshot.receiving != previous.receiving ||\n',
)

print("Home RTL identity/USB status fix applied.")
