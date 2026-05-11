#!/usr/bin/env python3

import os
import re
import subprocess
import sys

SNAPRAID_CONF = "/etc/snapraid.conf"
SNAPRAID_BIN = "/usr/bin/snapraid"
MAX_ATTEMPTS = 5


def error_exit(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    print("SnapRAID sync aborted.", file=sys.stderr)
    sys.exit(1)


def check_mount(path: str) -> None:
    if not os.path.ismount(path):
        error_exit(f"{path} is NOT mounted!")


def check_not_empty(path: str) -> None:
    if not os.path.isdir(path):
        return
    try:
        if not os.listdir(path):
            error_exit(f"{path} is mounted but EMPTY! Possible failed mount.")
    except PermissionError:
        error_exit(f"Cannot access {path}")


def parse_config(conf_path: str) -> tuple[list[str], list[str], list[str]]:
    data_paths: list[str] = []
    parity_paths: list[str] = []
    content_paths: list[str] = []

    data_re = re.compile(r"^data\s+\S+\s+(.+)$")
    parity_re = re.compile(r"^parity\s+(.+)$")
    content_re = re.compile(r"^content\s+(.+)$")

    try:
        with open(conf_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                m = data_re.match(line)
                if m:
                    data_paths.append(m.group(1))
                    continue

                m = parity_re.match(line)
                if m:
                    parity_paths.append(os.path.dirname(m.group(1)))
                    continue

                m = content_re.match(line)
                if m:
                    content_paths.append(os.path.dirname(m.group(1)))
                    continue
    except FileNotFoundError:
        error_exit(f"Config file {conf_path} not found!")

    return data_paths, parity_paths, content_paths


def main() -> None:
    data_paths, parity_paths, content_paths = parse_config(SNAPRAID_CONF)

    print("Checking DATA disks...")
    for path in data_paths:
        check_mount(path)
        check_not_empty(path)

    print("Checking PARITY disks...")
    for path in parity_paths:
        check_mount(path)

    print("Checking CONTENT paths...")
    for path in content_paths:
        if not os.path.isdir(path):
            error_exit(f"Content directory {path} does not exist!")
        if not os.access(path, os.W_OK):
            error_exit(f"Content directory {path} is not writable!")

    print("All SnapRAID paths verified.")

    success = False
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"Attempt {attempt}...")

        result = subprocess.run([SNAPRAID_BIN, "sync"])
        if result.returncode == 0:
            success = True
            break

        print("Sync failed, retrying...")

    if not success:
        error_exit(f"Sync failed after {MAX_ATTEMPTS} attempts")

    print("SnapRAID sync completed.")


if __name__ == "__main__":
    main()
