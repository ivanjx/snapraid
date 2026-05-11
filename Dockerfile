FROM python:3.12-slim

ARG SNAPRAID_VERSION=14.4

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
    && curl -fsSL -o /tmp/snapraid.deb \
        "https://github.com/amadvance/snapraid/releases/download/v${SNAPRAID_VERSION}/snapraid_${SNAPRAID_VERSION}-1_amd64.deb" \
    && apt-get install -y --no-install-recommends /tmp/snapraid.deb \
    && rm -f /tmp/snapraid.deb \
    && apt-get purge -y --auto-remove curl \
    && rm -rf /var/lib/apt/lists/*

COPY snapraid_sync.py /usr/local/bin/snapraid_sync.py

ENTRYPOINT ["python", "/usr/local/bin/snapraid_sync.py"]
