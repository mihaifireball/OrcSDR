#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one match, found {count}")
    path.write_text(text.replace(old, new, 1))
    print(f"updated {path.relative_to(ROOT)}")


hpp = ROOT / "apps/orcsdr-tab5/ui/settings_app.hpp"
cpp = ROOT / "apps/orcsdr-tab5/ui/settings_app.cpp"
main = ROOT / "apps/orcsdr-tab5/ui/main.cpp"

replace_once(
    hpp,
    "  char default_band[16]{};\n  uint32_t fm_frequency_hz = 0;\n\n  bool sd_ready = false;",
    "  char default_band[16]{};\n  uint32_t fm_frequency_hz = 0;\n  bool rtl_v3_connected = false;\n  int16_t rtl_v3_gain_db10 = -1;\n\n  bool sd_ready = false;",
)

replace_once(
    hpp,
    "  auto_start_changed,\n  graphics_changed\n  ,catalog_check",
    "  auto_start_changed,\n  graphics_changed,\n  rtl_v3_gain_step\n  ,catalog_check",
)

replace_once(
    cpp,
    '''  value_row("GRAPHICS DEFAULT", g_state.graphics_default ? "ON" : "OFF", 375);\n  value_row("GAIN / BIAS-TEE / CAL", "UNAVAILABLE", 425, kMuted);\n  button("TOGGLE AUTO-START", 330, 500, 260, 50, TFT_DARKCYAN);\n  button("TOGGLE GRAPHICS", 620, 500, 240, 50, TFT_DARKCYAN);''',
    '''  value_row("GRAPHICS DEFAULT", g_state.graphics_default ? "ON" : "OFF", 375);\n  if (g_state.rtl_v3_connected) {\n    char gain_value[24];\n    if (g_state.rtl_v3_gain_db10 < 0)\n      strlcpy(gain_value, "DEFAULT", sizeof(gain_value));\n    else\n      snprintf(gain_value, sizeof(gain_value), "%.1f dB",\n               g_state.rtl_v3_gain_db10 / 10.0f);\n    text("GAIN", 330, 420, TFT_WHITE, 2);\n    button("-", 820, 402, 72, 48, TFT_DARKGREY);\n    button(gain_value, 905, 402, 174, 48, TFT_NAVY);\n    button("+", 1092, 402, 72, 48, TFT_DARKCYAN);\n    value_row("BIAS-TEE / CAL", "UNAVAILABLE", 485, kMuted);\n  } else {\n    value_row("GAIN / BIAS-TEE / CAL", "UNAVAILABLE", 425, kMuted);\n  }\n  button("TOGGLE AUTO-START", 330, 555, 260, 50, TFT_DARKCYAN);\n  button("TOGGLE GRAPHICS", 620, 555, 240, 50, TFT_DARKCYAN);''',
)

replace_once(
    cpp,
    '''  const bool companion_changed = g_section == Section::companion &&\n      (g_state.web_console_enabled != state_value.web_console_enabled ||\n       g_state.web_console_listening != state_value.web_console_listening ||\n       strcmp(g_state.web_console_url, state_value.web_console_url) != 0);\n  g_state = state_value;''',
    '''  const bool companion_changed = g_section == Section::companion &&\n      (g_state.web_console_enabled != state_value.web_console_enabled ||\n       g_state.web_console_listening != state_value.web_console_listening ||\n       strcmp(g_state.web_console_url, state_value.web_console_url) != 0);\n  const bool radio_changed = g_section == Section::radio_defaults &&\n      (g_state.rtl_v3_connected != state_value.rtl_v3_connected ||\n       g_state.rtl_v3_gain_db10 != state_value.rtl_v3_gain_db10);\n  g_state = state_value;''',
)

replace_once(
    cpp,
    '''  if (companion_changed && g_edit == EditField::none && g_wifi_edit == WifiEdit::none)\n    draw_content();\n}''',
    '''  if (companion_changed && g_edit == EditField::none && g_wifi_edit == WifiEdit::none)\n    draw_content();\n  if (radio_changed && g_edit == EditField::none && g_wifi_edit == WifiEdit::none)\n    draw_content();\n}''',
)

replace_once(
    cpp,
    '''  } else if (g_section == Section::radio_defaults) {\n    if (hit(x, y, 330, 500, 260, 50)) {\n      g_state.auto_start_reception = !g_state.auto_start_reception;\n      draw_content();\n      return {ActionKind::auto_start_changed, g_state.auto_start_reception};\n    }\n    if (hit(x, y, 620, 500, 240, 50)) {\n      g_state.graphics_default = !g_state.graphics_default;\n      draw_content();\n      return {ActionKind::graphics_changed, g_state.graphics_default};\n    }\n  } else if (g_section == Section::companion) {''',
    '''  } else if (g_section == Section::radio_defaults) {\n    if (g_state.rtl_v3_connected && hit(x, y, 820, 402, 72, 48))\n      return {ActionKind::rtl_v3_gain_step, -1};\n    if (g_state.rtl_v3_connected && hit(x, y, 1092, 402, 72, 48))\n      return {ActionKind::rtl_v3_gain_step, 1};\n    if (hit(x, y, 330, 555, 260, 50)) {\n      g_state.auto_start_reception = !g_state.auto_start_reception;\n      draw_content();\n      return {ActionKind::auto_start_changed, g_state.auto_start_reception};\n    }\n    if (hit(x, y, 620, 555, 240, 50)) {\n      g_state.graphics_default = !g_state.graphics_default;\n      draw_content();\n      return {ActionKind::graphics_changed, g_state.graphics_default};\n    }\n  } else if (g_section == Section::companion) {''',
)

replace_once(
    main,
    "std::atomic<int> rtl_v3_gain_db10{0};",
    "std::atomic<int> rtl_v3_gain_db10{-1};",
)

replace_once(
    main,
    '''  state.fm_frequency_hz = rtl_saved_fm_hz;\n  state.sd_ready = g_sd_ready;''',
    '''  state.fm_frequency_hz = rtl_saved_fm_hz;\n  state.rtl_v3_connected = rtl_is_blog_v3.load(std::memory_order_acquire);\n  state.rtl_v3_gain_db10 = static_cast<int16_t>(\n      rtl_v3_gain_db10.load(std::memory_order_relaxed));\n  state.sd_ready = g_sd_ready;''',
)

replace_once(
    main,
    '''    case orcsdr::settings::ActionKind::graphics_changed:\n      settings_graphics_default = action.value != 0;\n      preferences.putBool("set_gfx", settings_graphics_default);\n      break;\n    case orcsdr::settings::ActionKind::web_console_changed:''',
    '''    case orcsdr::settings::ActionKind::graphics_changed:\n      settings_graphics_default = action.value != 0;\n      preferences.putBool("set_gfx", settings_graphics_default);\n      break;\n    case orcsdr::settings::ActionKind::rtl_v3_gain_step: {\n      if (!rtl_is_blog_v3.load(std::memory_order_acquire) || g_rtl == nullptr ||\n          action.value == 0) {\n        break;\n      }\n\n      int current = rtl_v3_gain_db10.load(std::memory_order_relaxed);\n      if (current < 0) current = 386;\n\n      size_t best = 0;\n      int best_delta = abs(current - kRtlV3GainStepsDb10[0]);\n      for (size_t i = 1; i < std::size(kRtlV3GainStepsDb10); ++i) {\n        const int delta = abs(current - kRtlV3GainStepsDb10[i]);\n        if (delta < best_delta) {\n          best = i;\n          best_delta = delta;\n        }\n      }\n\n      if (action.value < 0) {\n        if (best > 0) --best;\n      } else if (best + 1 < std::size(kRtlV3GainStepsDb10)) {\n        ++best;\n      }\n\n      const int requested = kRtlV3GainStepsDb10[best];\n      const esp_err_t gain_err = rtl_sdr_v4_esp_set_gain_db10(g_rtl, requested);\n      if (gain_err == ESP_OK) {\n        rtl_v3_gain_db10.store(requested, std::memory_order_relaxed);\n        Serial.printf("RTL_V3_GAIN_SETTINGS requested=%.1f dB queued\\n",\n                      static_cast<double>(requested) / 10.0);\n        orcsdr::settings::update(global_settings_state());\n      } else {\n        Serial.printf("RTL_V3_GAIN_SETTINGS_FAIL requested=%.1f dB error=%s\\n",\n                      static_cast<double>(requested) / 10.0,\n                      rtl_sdr_v4_esp_err_to_name(gain_err));\n      }\n      break;\n    }\n    case orcsdr::settings::ActionKind::web_console_changed:''',
)

print("RTL-SDR V3 Settings gain integration applied successfully.")
