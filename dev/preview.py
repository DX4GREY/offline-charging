#!/usr/bin/env python3
"""
Offline Charger UI Preview Tool
Generates sample rendering images (PNG) to test and review UI changes without hardware.
"""

import os
import sys

# Add bin/ to path to import render_frame
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_DIR, "bin"))

from importlib.machinery import SourceFileLoader
import cairo

daemon_path = os.path.join(REPO_DIR, "bin", "offline-charger")
mod = SourceFileLoader("offline_charger", daemon_path).load_module()

def generate_preview(capacity, is_chg, boot_prog=0.0, msg=None, sub_msg=None, telemetry=None, filename="preview.png"):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, mod.WIDTH, mod.HEIGHT)
    mod.render_frame(
        surface,
        capacity=capacity,
        is_chg=is_chg,
        boot_progress=boot_prog,
        custom_msg=msg,
        sub_msg=sub_msg,
        telemetry=telemetry
    )
    out_path = os.path.join(REPO_DIR, filename)
    surface.write_to_png(out_path)
    print(f"Generated preview: {out_path}")

if __name__ == "__main__":
    out_dir = os.path.join(REPO_DIR, "dev", "previews")
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Standard USB-PD Fast Charging (15W, 5V / 3A, 38.8°C)
    pd_telemetry = {
        "active_type": "PD",
        "supports_pps": True,
        "volts": 5.0,
        "amps": 3.0,
        "watts": 15.0,
        "temp_c": 38.8
    }
    generate_preview(65, True, telemetry=pd_telemetry, filename="dev/previews/pd_charging_65pct.png")

    # 2. PPS Fast Charging sample (18W, 9V / 2A, 40.2°C)
    pps_telemetry = {
        "active_type": "PD_PPS",
        "supports_pps": True,
        "volts": 9.0,
        "amps": 2.0,
        "watts": 18.0,
        "temp_c": 40.2
    }
    generate_preview(28, True, telemetry=pps_telemetry, filename="dev/previews/pps_charging_28pct.png")

    # 3. High Temperature Warning (> 45°C)
    hot_telemetry = {
        "active_type": "PD",
        "supports_pps": False,
        "volts": 5.0,
        "amps": 2.8,
        "watts": 14.0,
        "temp_c": 46.5
    }
    generate_preview(88, True, telemetry=hot_telemetry, filename="dev/previews/hot_charging_warning.png")

    # 4. Cable Disconnected Countdown
    generate_preview(45, False, msg="Cable Disconnected", sub_msg="Powering off in 3s...", filename="dev/previews/unplugged.png")

    # 5. Long Press Power Button to Boot Kali
    generate_preview(75, True, boot_prog=0.75, telemetry=pd_telemetry, filename="dev/previews/booting.png")
    
    print("All preview screenshots generated in dev/previews/")
