# MediaStack on ZimaOS (one custom app per service)

Converted from `no-download-vpn/docker-compose.yaml`. Each folder in `apps/` is a standalone
ZimaOS custom-app compose file (with an `x-casaos` block). Regenerate with `python3 zimaos/generate.py`.

**Dropped** (ZimaOS provides its own UI/ports): Traefik, Authentik, CrowdSec, Postgres, Valkey,
Guacamole, Headscale/Tailscale/Headplane, Prometheus/Grafana, certs-dumper.

## Install
ZimaOS dashboard -> **+** -> *Install a customized app* -> import `apps/<app>/docker-compose.yml`.

## Before you install
- Media root is `/DATA/Media` (mounted as `/data`). Keep the TRaSH-style layout
  (`torrents/`, `usenet/`, `media/`) so hardlinks work. Change `MEDIA` in `generate.py` to relocate.
- Configs live in `/DATA/AppData/$AppID/` (ZimaOS fills in `$AppID`).
- PUID/PGID `1000`, TZ `Europe/Zurich`, theme `nord`: edit in `generate.py` if wrong.
- Apps no longer share a docker network. Reach siblings via the ZimaOS IP and published port
  (e.g. `http://<zima-ip>:7878` for Radarr in Prowlarr/Seerr).
- **unpackerr**: replace `ZIMA_IP` and every `CHANGE_ME` API key after install.
- **plex**: set `PLEX_CLAIM` (4-minute token) on first install, or claim via the UI.
- Images use floating tags as in the original stack; pin digests if you want reproducibility.
- Ports follow the original `.env` (`WEBUI_PORT_*`). Check they don't clash with other ZimaOS apps.
