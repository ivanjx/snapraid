#!/usr/bin/env python3

import argparse
import os
import re
import subprocess
import sys

SNAPRAID_CONF = "/etc/snapraid.conf"
SNAPRAID_BIN = "/usr/bin/snapraid"
MAX_ATTEMPTS = 5


def error_exit(message: str, command: str = "sync") -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    print(f"SnapRAID {command} aborted.", file=sys.stderr)
    sys.exit(1)


def check_mount(path: str, command: str, content_files: list[str] | None = None) -> None:
    if content_files:
        sep = os.sep
        for cf in content_files:
            if cf.startswith(path + sep) and os.path.isfile(cf):
                return
    error_exit(f"{path} is NOT mounted!", command)


def parse_config(conf_path: str) -> tuple[list[str], list[str], list[str], list[str]]:
    data_paths: list[str] = []
    parity_paths: list[str] = []
    content_paths: list[str] = []
    content_files: list[str] = []

    data_re = re.compile(r"^data\s+\S+\s+(.+)$")
    parity_re = re.compile(r"^parity\s+(.+)$")
    content_re = re.compile(r"^content\s+(.+)$")

    try:
        with open(conf_path, "r") as f:
            for line in f:
                line = line.split("#", 1)[0].strip()
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
                    cf = m.group(1)
                    content_files.append(cf)
                    content_paths.append(os.path.dirname(cf))
                    continue
    except FileNotFoundError:
        error_exit(f"Config file {conf_path} not found!")

    return data_paths, parity_paths, content_paths, content_files


def main() -> None:
    parser = argparse.ArgumentParser(description="SnapRAID wrapper")
    parser.add_argument(
        "command",
        nargs="?",
        default="sync",
        choices=["sync", "fix"],
        help="SnapRAID command to run (default: sync)",
    )
    parser.add_argument(
        "-f",
        "--filter",
        metavar="PATH",
        help="Filter by file/folder path (only for fix command)",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initial run"
    )
    args = parser.parse_args()
    command = args.command

    if args.filter and command != "fix":
        error_exit("--filter can only be used with the fix command", command)

    data_paths, parity_paths, content_paths, content_files = parse_config(SNAPRAID_CONF)

    if not args.init:
        print("Checking DATA disks...")
        for path in data_paths:
            check_mount(path, command, content_files)

        print("Checking PARITY disks...")
        for path in parity_paths:
            if not os.path.isdir(path):
                error_exit(f"Parity directory {path} does not exist!", command)
            if not os.access(path, os.W_OK):
                error_exit(f"Parity directory {path} is not writable!", command)

        print("Checking CONTENT paths...")
        for path in content_paths:
            if not os.path.isdir(path):
                error_exit(f"Content directory {path} does not exist!", command)
            if not os.access(path, os.W_OK):
                error_exit(f"Content directory {path} is not writable!", command)

        print("All SnapRAID paths verified.")

    if command == "fix":
        cmd = [SNAPRAID_BIN, "-c", SNAPRAID_CONF, command]
        if args.filter:
            cmd.extend(["-f", args.filter])
        print("Running fix...")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            error_exit("Fix failed", command)
    else:
        success = False
        for attempt in range(1, MAX_ATTEMPTS + 1):
            print(f"Attempt {attempt}...")

            result = subprocess.run([SNAPRAID_BIN, "-c", SNAPRAID_CONF, command])
            if result.returncode == 0:
                success = True
                break

            print("Sync failed, retrying...")

        if not success:
            error_exit(
                f"Sync failed after {MAX_ATTEMPTS} attempts", command
            )

    print(f"SnapRAID {command} completed.")


if __name__ == "__main__":
    main()
