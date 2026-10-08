#!/usr/bin/env python3
"""
Input Event, Power Supply, and USB-PD Telemetry Diagnostic Tool
Monitors power button, volume keys, battery status, and USB Power Delivery (PD/PPS) in real time.
"""

import os
import sys
import glob
import time
import struct
import select

def check_power_supplies():
    print("=== Power Supply Nodes ===")
    for path in glob.glob("/sys/class/power_supply/*"):
        name = os.path.basename(path)
        type_file = os.path.join(path, "type")
        dev_type = open(type_file).read().strip() if os.path.exists(type_file) else "Unknown"
        print(f"[{name}] (Type: {dev_type})")
        for prop in ["capacity", "status", "online", "current_now", "voltage_now", "usb_type", "temp"]:
            prop_file = os.path.join(path, prop)
            if os.path.exists(prop_file):
                val = open(prop_file).read().strip()
                if prop == "temp":
                    try:
                        val = f"{int(val)/10.0:.1f}°C"
                    except Exception:
                        pass
                elif prop in ["voltage_now", "voltage_max"]:
                    try:
                        val = f"{int(val)/1000000.0:.2f}V"
                    except Exception:
                        pass
                elif prop in ["current_now", "current_max"]:
                    try:
                        val = f"{int(val)/1000000.0:.2f}A"
                    except Exception:
                        pass
                print(f"   {prop}: {val}")
    print()

def check_usb_pd():
    print("=== USB Power Delivery (PD / PPS) Status ===")
    pd_dirs = glob.glob("/sys/class/usb_power_delivery/*")
    if not pd_dirs:
        print("No usb_power_delivery devices found in sysfs.\n")
        return

    for pd_path in pd_dirs:
        pd_name = os.path.basename(pd_path)
        print(f"[{pd_name}]")
        
        # Source capabilities
        src_caps = glob.glob(os.path.join(pd_path, "source-capabilities", "*"))
        for cap in src_caps:
            c_name = os.path.basename(cap)
            if os.path.isdir(cap) and c_name != "power":
                volt_f = os.path.join(cap, "voltage")
                curr_f = os.path.join(cap, "maximum_current")
                v = open(volt_f).read().strip() if os.path.exists(volt_f) else "?"
                c = open(curr_f).read().strip() if os.path.exists(curr_f) else "?"
                print(f"   Source Capability ({c_name}): {v} @ {c}")

        # Sink capabilities
        sink_caps = glob.glob(os.path.join(pd_path, "sink-capabilities", "*"))
        for cap in sink_caps:
            c_name = os.path.basename(cap)
            if os.path.isdir(cap) and c_name != "power":
                volt_f = os.path.join(cap, "voltage")
                curr_f = os.path.join(cap, "operational_current")
                v = open(volt_f).read().strip() if os.path.exists(volt_f) else "?"
                c = open(curr_f).read().strip() if os.path.exists(curr_f) else "?"
                print(f"   Sink Capability ({c_name}): {v} @ {c}")
    print()

def monitor_inputs():
    print("=== Monitoring Input Devices (Press Ctrl+C to exit) ===")
    inputs = glob.glob("/dev/input/by-path/*") + glob.glob("/dev/input/event*")
    inputs = list(set(inputs))
    
    fds = {}
    for path in inputs:
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
            fds[fd] = path
            print(f"Listening on: {path}")
        except Exception:
            pass

    if not fds:
        print("No input devices could be opened (try running with sudo).")
        return

    try:
        while True:
            r, _, _ = select.select(list(fds.keys()), [], [], 1.0)
            for fd in r:
                path = fds[fd]
                try:
                    while True:
                        data = os.read(fd, 24)
                        if len(data) < 24:
                            break
                        sec, usec, ev_type, ev_code, ev_val = struct.unpack("qqHHi", data)
                        if ev_type == 1: # EV_KEY
                            action = "RELEASED" if ev_val == 0 else ("PRESSED" if ev_val == 1 else "REPEAT")
                            key_name = "KEY_POWER" if ev_code == 116 else f"CODE_{ev_code}"
                            print(f"[{time.strftime('%H:%M:%S')}] {path} -> {key_name} ({action})")
                except (BlockingIOError, OSError):
                    pass
    except KeyboardInterrupt:
        print("\nExiting input monitor.")
    finally:
        for fd in fds:
            os.close(fd)

if __name__ == "__main__":
    check_power_supplies()
    check_usb_pd()
    monitor_inputs()
