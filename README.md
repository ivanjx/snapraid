# SnapRAID Docker

Docker image that runs [SnapRAID](https://github.com/amadvance/snapraid) sync with pre-flight safety checks, downloaded from the official GitHub releases.

## Build

```bash
docker build -t snapraid-sync .
```

To pin a different SnapRAID version:

```bash
docker build --build-arg SNAPRAID_VERSION=14.3 -t snapraid-sync .
```

## Run

### Docker

Initial run to initialize snapraid:

```bash
docker run --rm \
  -v /etc/snapraid.conf:/etc/snapraid.conf:ro \
  -v /mnt/disk1:/mnt/disk1 \
  -v /mnt/disk2:/mnt/disk2 \
  -v /mnt/parity1:/mnt/parity1 \
  ghcr.io/ivanjx/snapraid:latest --init
```

Subsequent runs:

```bash
docker run --rm \
  -v /etc/snapraid.conf:/etc/snapraid.conf:ro \
  -v /mnt/disk1:/mnt/disk1 \
  -v /mnt/disk2:/mnt/disk2 \
  -v /mnt/parity1:/mnt/parity1 \
  ghcr.io/ivanjx/snapraid:latest
```

To run `snapraid fix` instead:

```bash
docker run --rm \
  -v /etc/snapraid.conf:/etc/snapraid.conf:ro \
  -v /mnt/disk1:/mnt/disk1 \
  -v /mnt/disk2:/mnt/disk2 \
  -v /mnt/parity1:/mnt/parity1 \
  ghcr.io/ivanjx/snapraid:latest fix
```

To fix only a specific file or folder:

```bash
docker run --rm \
  -v /etc/snapraid.conf:/etc/snapraid.conf:ro \
  -v /mnt/disk1:/mnt/disk1 \
  -v /mnt/disk2:/mnt/disk2 \
  -v /mnt/parity1:/mnt/parity1 \
  ghcr.io/ivanjx/snapraid:latest fix -f /mnt/disk1/some/file
```

### Docker Compose

```yaml
services:
  snapraid:
    image: ghcr.io/ivanjx/snapraid:latest
    volumes:
      - /etc/snapraid.conf:/etc/snapraid.conf:ro
      - /mnt/disk1:/mnt/disk1
      - /mnt/disk2:/mnt/disk2
      - /mnt/parity1:/mnt/parity1
    restart: "no"
    profiles:
      - snapraid
```

## Configuration

Example `/etc/snapraid.conf` matching the mounts above:

```ini
# Parity file
parity /mnt/parity1/snapraid.parity

# Content files (one per data disk, plus parity)
content /mnt/disk1/.snapraid.content
content /mnt/disk2/.snapraid.content
content /mnt/parity1/.snapraid.content

# Data disks
data d1 /mnt/disk1
data d2 /mnt/disk2
```

## What it does

1. Parses `/etc/snapraid.conf` for `data`, `parity`, and `content` paths
2. Verifies every data disk is mounted and not empty (guards against stale mounts)
3. Verifies every parity disk is mounted
4. Verifies every content directory exists and is writable
5. Runs the specified command: `sync` (default, with up to 5 retries) or `fix` (no retries, optionally scoped to a path with `-f`)
