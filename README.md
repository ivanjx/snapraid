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

```bash
docker run --rm \
  -v /etc/snapraid.conf:/etc/snapraid.conf:ro \
  -v /mnt/disk1:/mnt/disk1 \
  -v /mnt/disk2:/mnt/disk2 \
  -v /mnt/parity1:/mnt/parity1 \
  ghcr.io/ivanjx/snapraid:latest
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

## What it does

1. Parses `/etc/snapraid.conf` for `data`, `parity`, and `content` paths
2. Verifies every data disk is mounted and not empty (guards against stale mounts)
3. Verifies every parity disk is mounted
4. Verifies every content directory exists and is writable
5. Runs `snapraid sync` with up to 5 retries on failure
