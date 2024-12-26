#!/usr/bin/env python3

import platform
import socket
import psutil
import subprocess
import time
import argparse
import json
import shutil
import re
import os
import sys
import datetime
import logging
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path

# currently unused
CONFIG_DIR = Path.home() / '.config' / 'pyrfetch'
CONFIG_FILE = CONFIG_DIR / 'config.json'
CACHE_DIR = CONFIG_DIR / 'cache'
LOG_FILE = CONFIG_DIR / 'sysinfo.log'

# CONFIG_DIR = os.path.join(os.path.expanduser("~"), '.config', 'pyrfetch')
# CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
# CACHE_DIR = os.path.join(CONFIG_DIR, 'cache')
# LOG_FILE = os.path.join(CONFIG_DIR, 'sysinfo.log')

COLORS = {
    "default": "\033[0m",
    "white": "\033[37m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "purple": "\033[35m",
    "cyan": "\033[36m",
    "pink": "\033[95m",
    "orange": "\033[91m",
    "lime": "\033[92m",
    "azure": "\033[94m",
    "magenta": "\033[95m",
    "turquoise": "\033[96m",
    "bright_white": "\033[97m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "italic": "\033[3m",
    "underline": "\033[4m",
    "blink": "\033[5m",
    "reverse": "\033[7m",
    "hidden": "\033[8m",
    "strike": "\033[9m"
}

DISTRO_COLORS = {
    "Arch":      COLORS["bright_cyan"],
    "Gentoo":    COLORS["dim"],
    "Ubuntu":    COLORS["orange"],
    "Fedora":    COLORS["cyan"],
    "Kali":      COLORS["blue"],
    "macOS":     COLORS["pink"],
    "Debian":    COLORS["bright_red"],
    "Mint":      COLORS["bright_green"],
    "Pop":       COLORS["bright_blue"],
    "Manjaro":   COLORS["green"],
    "Endeavour": COLORS["purple"],
    "OpenSUSE":  COLORS["lime"],
    "RedHat":    COLORS["red"],
    "Zorin":     COLORS["blue"],
    "Default":   COLORS["default"]
}

ASCII_ARTS = {
    "Arch": [
        "      /\\           ",
        "     /  \\          ",
        "    /    \\         ",
        "   /      \\        ",
        "  /   ,,   \\       ",
        " /   |  |   \\      ",
        "/_-''    ''-_\\     "
    ],
    "Gentoo": [
        "   .-----.         ",
        " ./       \\.       ",
        "/   .---.   \\      ",
        "|  /     \\  |      ",
        "|  \\     /  |      ",
        "\\   `---'   /      ",
        " `.___.__.'        "
    ],
    "Ubuntu": [
        "    _____         ",
        "   /  __ \\        ",
        "  |  /  \\ |       ",
        "  |  \\__/ |       ",
        "   \\_____/        ",
        "                  ",
        "                  "
    ],
    "Fedora": [
        "      _____       ",
        "     /   __\\      ",
        "    |  /          ",
        "    |  \\___       ",
        "    |  ____\\      ",
        "    |  |          ",
        "     \\__\\         "
    ],
    "Kali": [
        " __         __    ",
        " \\ \\       / /    ",
        "  \\ \\.---./ /     ",
        "  |  _   _  |     ",
        "  |   \\ /   |     ",
        "  |   O O   |     ",
        "   \\  \\^/  /      ",
        "    \\     /       ",
        "     `---'        "
    ],
    "macOS": [
        "         /\\       ",
        "        /_/       ",
        "   ____   ____    ",
        "  /    \\_/    \\   ",
        "  |          __|  ",
        "  |         /     ",
        "  |         \\_    ",
        "   \\     _    |   ",
        "     \\__/ \\___/   "
    ],
    "Debian": [
        "        ____          ",
        "       /  __ \\        ",
        "      |  /   |        ",
        "      |  \\___/        ",
        "      \\               ",
        "       \\__            ",
        "                      "
    ],
    "Mint": [
        " _    ___________    ",
        "| |  /  __    _   \\  ",
        "| |  | |  |  | |  |  ",
        "| |  | |  |  | |  |  ",
        "| |  | |  |  | |  |  ",
        "| |  | |  |  | |  |  ",
        "| |  |_|  |__| |  |  ",
        "| \\____________|  |  ",
        "\\_________________|  "
    ],
    "Pop": [
        "                  ",
        "  ▄█████▄▄ ██     ",
        "  ██    ██ ██     ",
        "  ██    ██ ██     ",
        "  ██████▀▀ ██     ",
        "  ██              ",
        "  ██       ██     "
    ],
    "Manjaro": [
        "█████████ ████    ",   
        "████▀▀▀▀▀ ████    ", 
        "████ ████ ████    ", 
        "████ ████ ████    ",  
        "████ ████ ████    ",  
        "████ ████ ████    "
    ],
    "Endeavour": [
        "                    ",
        "      //\\           ",
        "    / /  \\\\         ",
        "   / /    \\ \\       ",
        "  / /      \\  \\     ",
        " / /        \\  \\    ",
        "/_/__________\\  |   ",
        " /_____________/    "
    ],
    "OpenSUSE": [
        "   _______       ",
        "  /       \\      ",
        " /    __   \\     ",
        "|   /  \\   |     ",
        "|   \\__/   |     ",
        " \\         /     ",
        "  \\_______/      "
    ],
    "RedHat": [
        "                  ",
        "                  ",
        "     RED HAT      ",  
        "      _____       ",  
        "    _|     |__    ",  
        "   \\_________/    ", 
        "                  "
    ],
    "Zorin": [
        "                  ",
        "                  ",
        "    ▀▀▀▀▀▀▀██     ",
        "         ██       ",
        "       ██         ",
        "     ██           ",
        "    ▀▀▀▀▀▀▀▀▀     "
    ],
    "Default": [
        "   _______       ",
        "  |       |      ",
        "  |  [ ]  |      ",
        "  |       |      ",
        "  |  ___  |      ",
        "  | |   | |      ",
        "  |_|   |_|      "
    ]
}

class SystemInfo:
    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                          format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('SystemInfo')

    def get_os_name(self): #CHEKED
        os_patterns = {
            "arch": "Arch", "gentoo": "Gentoo", "ubuntu": "Ubuntu", "fedora": "Fedora",
            "kali": "Kali", "debian": "Debian", "linuxmint": "Mint", "pop!_os": "Pop",
            "pop_os": "Pop", "manjaro": "Manjaro", "endeavour": "Endeavour",
            "opensuse": "OpenSUSE", "red hat": "RedHat", "zorin": "Zorin"
        }
        try:
            with open("/etc/os-release", "r") as file:
                content = file.read().lower()
                for pattern, name in os_patterns.items():
                    if pattern in content:
                        return name
        except FileNotFoundError:
            if platform.system() == "Darwin":
                return "macOS"
        return "Default"

    def get_cpu_info(self): #CHEKED
        if platform.system() == "Darwin":
            try:
                return subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                                   capture_output=True, text=True, check=True).stdout.strip()
            except:
                pass
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":")[1].strip()
        except:
            pass 
        return "Unknown"

    def get_gpu_info(self): #CHEKED
        if shutil.which("nvidia-smi"):
            try:
                result = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                                     stdout=subprocess.PIPE, text=True, check=True)
                return result.stdout.strip()
            except:
                pass
        try:
            result = subprocess.run(["lspci"], stdout=subprocess.PIPE, text=True, check=True)
            for line in result.stdout.splitlines():
                if any(x in line for x in ["VGA compatible controller", "3D controller"]):
                    return line.split(":")[2].strip()
        except:
            pass
        return "N/A"

    def get_network_info(self):
        interfaces = {}
        try:
            for iface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        interfaces[iface] = addr.address
        except Exception as e:
            self.logger.error(f"Network error: {e}")
        return interfaces

    def get_battery_info(self):
        try:
            battery = psutil.sensors_battery()
            if battery:
                return f"{battery.percent}% {'(Charging)' if battery.power_plugged else ''}"
        except:
            pass
        return "N/A"

    def get_distro_color(self, color, os_name):
        if (color == "default"):
            return DISTRO_COLORS.get(os_name, DISTRO_COLORS["Default"])
        return COLORS.get(color, COLORS["default"])
    
    def get_ascii_art(self, ascii, os_name):
        if (ascii == "default"):
            return ASCII_ARTS.get(os_name, ASCII_ARTS["Default"])
        else:
            try:
                ascii_file = open(ascii, "r")
                ascii_lines = ascii_file.readlines()
                final_ascii_lines = []
                for ascii_line in ascii_lines:
                    ascii_line = ascii_line.replace("\n", "")
                    final_ascii_lines.append(ascii_line)
                return final_ascii_lines
                
            except Exception as e:
                self.logger.error(f"File Read Error: {e}")

    def format_uptime(self, seconds):
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        if days:
            return f"{days}d {hours}h {minutes}m"
        return f"{hours}h {minutes}m {seconds}s"

    def get_system_info(self, show_percentage=False, include_disk=False, include_temp=False,
                       export_file=None, distro=None, color="default", ascii="default"):
        os_name = distro if distro else self.get_os_name()
        kernel = platform.release()
        hostname = socket.gethostname()
        uptime = self.format_uptime(int(time.time() - psutil.boot_time()))
        cpu_name = self.get_cpu_info()
        gpu = self.get_gpu_info()
        
        ram = psutil.virtual_memory()
        ram_info = f"{ram.percent}%" if show_percentage else f"{ram.used/(1024**3):.1f}GB/{ram.total/(1024**3):.1f}GB"
        
        disk_info = "N/A"
        if include_disk:
            disk = psutil.disk_usage('/')
            disk_info = f"{disk.used/(1024**3):.1f}/{disk.total/(1024**3):.1f}GB ({disk.percent}%)"

        temp = "N/A"
        if include_temp:
            try:
                sensors = psutil.sensors_temperatures()
                if 'coretemp' in sensors:
                    temp = f"{sensors['coretemp'][0].current}°C"
            except:
                pass

        infoLabel = [
            f"OS: ",
            f"Kernel: ",
            f"Hostname: ",
            f"Uptime: ",
            f"RAM: ",
            f"CPU: ",
            f"GPU: ",
            f"Disk: ",
            f"Temp: ",
            "",
            ""
        ]
        info = [
            f"{os_name}",
            f"{kernel}",
            f"{hostname}",
            f"{uptime}",
            f"{ram_info}",
            f"{cpu_name}",
            f"{gpu}",
            f"{disk_info}",
            f"{temp}",
            "",
            ""
        ]

        ascii_art = self.get_ascii_art(ascii=ascii, os_name=os_name)
        #ascii_art = ASCII_ARTS.get(os_name, ASCII_ARTS["Default"])
        color_code = self.get_distro_color(color=color, os_name=os_name)

        print("")
        for i, art_line in enumerate(ascii_art):
            info_line = info[i] if i < len(info) else ""
            info_label_line = infoLabel[i] if i < len(infoLabel) else ""
            print(f"{color_code}{art_line}{info_label_line}{COLORS['default']}{info_line}")
        print("")

        if export_file:
            export_data = {k: v.split(": ")[1] for k, v in zip(
                ["OS", "Kernel", "Hostname", "Uptime", "RAM", "CPU", "GPU", "Disk", "Temp"],
                info[:9]
            )}
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Display system information with ASCII art")
    parser.add_argument("--percentage", action="store_true", help="Show RAM usage as percentage")
    parser.add_argument("--disk", action="store_true", help="Include disk information")
    parser.add_argument("--temp", action="store_true", help="Include temperature information")
    parser.add_argument("--export", type=str, help="Export information to JSON file")
    parser.add_argument("--distro", type=str, choices=ASCII_ARTS.keys(), help="Manually specify distribution")
    parser.add_argument("--color", type=str, choices=COLORS.keys(), default="default", help="Choose ASCII art color")
    parser.add_argument("--watch", action="store_true", help="Watch mode with live updates")
    parser.add_argument("--interval", type=int, default=2, help="Update interval for watch mode")
    parser.add_argument("--ascii", type=str, default="default", help="Path to a .txt containing ascii")

    args = parser.parse_args()
    sys_info = SystemInfo()

    try:
        while True:
            sys_info.get_system_info(
                args.percentage, args.disk, args.temp,
                args.export, args.distro, args.color, args.ascii
            )
            if not args.watch:
                break
            time.sleep(args.interval)
            os.system("clear")
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
