#!/usr/bin/env python3
"""Generate one ZimaOS/CasaOS custom-app compose file per MediaStack app.

Run from the repo root:  python3 zimaos/generate.py
Output: zimaos/apps/<app>/docker-compose.yml
"""
import pathlib

TZ = "Europe/Zurich"
MEDIA = "/DATA/Media"          # shared media root, mounted as /data in the *arr/download apps
ICON = "https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/{}.png"
THEME = "nord"

LSIO = {"PUID": "1000", "PGID": "1000", "TZ": TZ}
def tp(app):  # theme.park mod, same as the original stack
    return {"DOCKER_MODS": f"ghcr.io/themepark-dev/theme.park:{app}", "TP_THEME": THEME}

CFG = ("config", "/config")
DATA = ("media", "/data")      # whole media root
# (name, title, image, ui_port, ports[(host,container,proto)], volumes, env, icon, extra)
APPS = [
 dict(name="bazarr", img="lscr.io/linuxserver/bazarr:latest", port=6767, cport=6767, vols=[CFG, DATA], env={**LSIO, **tp("bazarr")}),
 dict(name="chromium", img="lscr.io/linuxserver/chromium:latest", port=3650, cport=3650, vols=[CFG],
      env={**LSIO, "TITLE": "MediaStack Chromium", "CUSTOM_PORT": "3650", "CHROME_CLI": "https://github.com/geekau/mediastack/"}, extra={"shm_size": "1gb"}),
 dict(name="ddns-updater", img="qmcgaw/ddns-updater:latest", port=8310, cport=8310, vols=[("config", "/updater/data")],
      env={"TZ": TZ, "UMASK": "0002", "PERIOD": "5m", "UPDATE_COOLDOWN_PERIOD": "5m", "LISTENING_ADDRESS": ":8310", "ROOT_URL": "/", "BACKUP_PERIOD": "0", "BACKUP_DIRECTORY": "/updater/data", "LOG_LEVEL": "info"},
      extra={"user": "1000:1000"}),
 dict(name="filebot", img="rednoah/filebot:xpra", port=5454, cport=5454, vols=[("filebot-media", "/filebot"), ("config", "/data/filebot")],
      env={**LSIO, "UMASK": "0002", "DARK_MODE": "1"}),
 dict(name="flaresolverr", img="ghcr.io/flaresolverr/flaresolverr:latest", port=8191, cport=8191, vols=[],
      env={"LOG_LEVEL": "info", "LOG_HTML": "false", "CAPTCHA_SOLVER": "none", "TZ": TZ}),
 dict(name="heimdall", img="lscr.io/linuxserver/heimdall:latest", port=2080, cport=80, vols=[CFG], env={**LSIO, "UMASK": "0002"}),
 dict(name="homarr", img="ghcr.io/ajnart/homarr:latest", port=3200, cport=7575,
      vols=[("sock", "/var/run/docker.sock"), ("config/configs", "/app/data/configs"), ("config/icons", "/app/public/icons"), ("config/data", "/data")],
      env={**LSIO, "UMASK": "0002"}),
 dict(name="homepage", img="ghcr.io/gethomepage/homepage:latest", port=3000, cport=3000,
      vols=[("sock", "/var/run/docker.sock"), ("config", "/app/config")],
      env={"UMASK": "0002", "TZ": TZ, "HOMEPAGE_ALLOWED_HOSTS": "*"}),
 dict(name="jellyfin", img="lscr.io/linuxserver/jellyfin:latest", port=8096, cport=8096, vols=[CFG, ("media-sub", "/data/media")], env={**LSIO, "UMASK": "0002"}),
 dict(name="lidarr", img="lscr.io/linuxserver/lidarr:latest", port=8686, cport=8686, vols=[CFG, DATA], env={**LSIO, **tp("lidarr")}),
 dict(name="mylar", img="lscr.io/linuxserver/mylar3:latest", port=8090, cport=8090, vols=[CFG, DATA], env={**LSIO, **tp("mylar3")}, icon="mylar3"),
 dict(name="plex", img="lscr.io/linuxserver/plex:latest", port=32400, cport=32400, vols=[CFG, ("media-sub", "/data/media")],
      env={**LSIO, "UMASK": "0002", "VERSION": "docker", "PLEX_CLAIM": ""}, scheme="http", index="/web"),
 dict(name="portainer", img="portainer/portainer-ce:latest", port=9000, cport=9000, vols=[("sock", "/var/run/docker.sock"), ("config", "/data")], env={}),
 dict(name="prowlarr", img="lscr.io/linuxserver/prowlarr:develop", port=9696, cport=9696, vols=[CFG], env={**LSIO, **tp("prowlarr")}),
 dict(name="qbittorrent", img="lscr.io/linuxserver/qbittorrent:latest", port=8200, cport=8200, vols=[CFG, DATA],
      env={**LSIO, "UMASK": "0002", "WEBUI_PORT": "8200", **tp("qbittorrent")},
      ports=[(6881, 6881, "tcp"), (6881, 6881, "udp")]),
 dict(name="radarr", img="lscr.io/linuxserver/radarr:latest", port=7878, cport=7878, vols=[CFG, DATA], env={**LSIO, **tp("radarr")}),
 dict(name="readarr", img="lscr.io/linuxserver/readarr:0.4.18-develop", port=8787, cport=8787, vols=[CFG, DATA], env={**LSIO, **tp("readarr")}),
 dict(name="sabnzbd", img="lscr.io/linuxserver/sabnzbd:latest", port=8100, cport=8080, vols=[CFG, DATA], env={**LSIO, **tp("sabnzbd")}),
 dict(name="seerr", img="ghcr.io/seerr-team/seerr:latest", port=5055, cport=5055, vols=[("config", "/app/config")], env={"TZ": TZ}),
 dict(name="sonarr", img="lscr.io/linuxserver/sonarr:latest", port=8989, cport=8989, vols=[CFG, DATA], env={**LSIO, **tp("sonarr")}),
 dict(name="tdarr", img="ghcr.io/haveagitgat/tdarr:latest", port=8265, cport=8265,
      vols=[("media-sub", "/data/media"), ("config/server", "/app/server"), ("config/configs", "/app/configs"), ("config/logs", "/app/logs"), ("config/temp", "/temp")],
      env={**LSIO, "UMASK": "0002", "serverIP": "0.0.0.0", "serverPort": "8266", "webUIPort": "8265", "internalNode": "true", "nodeID": "Tdarr_Server"},
      ports=[(8266, 8266, "tcp")]),
 dict(name="whisparr", img="ghcr.io/hotio/whisparr:nightly", port=6969, cport=6969, vols=[CFG, DATA], env={**LSIO, "UMASK": "0002"}),
]

# Unpackerr: sibling apps are reached through the ZimaOS host IP (separate compose projects
# do not share a docker network). Edit ZIMA_IP + API keys after install.
UNPACKERR_ENV = {
    "UMASK": "0002", "TZ": TZ, "UN_INTERVAL": "2m", "UN_START_DELAY": "1m", "UN_RETRY_DELAY": "5m",
    "UN_MAX_RETRIES": "3", "UN_PARALLEL": "1", "UN_FILE_MODE": "0644", "UN_DIR_MODE": "2755",
    "UN_LOG_FILE": "/config/unpackerr.log", "UN_WEBSERVER_METRICS": "true", "UN_WEBSERVER_LISTEN_ADDR": "0.0.0.0:5656",
    "UN_FOLDER_0_PATH": "/data/torrents/complete", "UN_FOLDER_0_DELETE_AFTER": "10m",
}
for app, port, path in [("SONARR", 8989, "/data/torrents/tv"), ("RADARR", 7878, "/data/torrents/movies"),
                        ("LIDARR", 8686, "/data/torrents/music"), ("READARR", 8787, "/data/torrents/books"),
                        ("MYLAR", 8090, "/data/torrents/comics"), ("WHISPARR", 6969, "/data/torrents/xxx")]:
    UNPACKERR_ENV.update({f"UN_{app}_0_URL": f"http://ZIMA_IP:{port}", f"UN_{app}_0_API_KEY": "CHANGE_ME",
                          f"UN_{app}_0_PATHS_0": path, f"UN_{app}_0_PROTOCOLS": "torrent",
                          f"UN_{app}_0_TIMEOUT": "10s", f"UN_{app}_0_DELETE_DELAY": "5m"})
APPS.append(dict(name="unpackerr", img="golift/unpackerr:latest", port=5656, cport=5656, vols=[("config", "/config"), DATA],
                 env=UNPACKERR_ENV, extra={"user": "1000:1000"}, scheme="http", index="/metrics"))

def q(v):  # always quote env values
    return '"' + str(v).replace("\\", "\\\\").replace('"', '\\"').replace("$", "$$") + '"'

def render(a):
    n = a["name"]; icon = a.get("icon", n)
    L = ["services:", f"  {n}:", f"    container_name: {n}", f"    image: {a['img']}", "    restart: unless-stopped"]
    for k, v in a.get("extra", {}).items():
        if k in ("user", "shm_size"): L.append(f"    {k}: {q(v) if k=='user' else v}")
    if a["env"]:
        L.append("    environment:")
        L += [f"      {k}: {q(v)}" for k, v in a["env"].items()]
    L.append("    ports:")
    ports = [(a["port"], a["cport"], "tcp")] + a.get("ports", [])
    for h, c, p in ports:
        L += [f"      - protocol: {p}", f'        published: "{h}"', f"        target: {c}"]
    if a["vols"]:
        L.append("    volumes:")
        for sub, tgt in a["vols"]:
            if sub == "sock": src = "/var/run/docker.sock"
            elif sub == "media": src = MEDIA
            elif sub == "media-sub": src = MEDIA + "/media"
            elif sub == "filebot-media": src = MEDIA + "/filebot"
            else: src = "/DATA/AppData/$AppID/" + sub
            L += [f"      - source: {src}", f"        target: {tgt}", "        type: bind"]
    L.append("    network_mode: bridge")
    L += ["x-casaos:", f"  icon: {ICON.format(icon)}", f"  id: mediastack-{n}", f"  index: {a.get('index', '/')}",
          f"  main: {n}", f'  port_map: "{a["port"]}"', f"  scheme: {a.get('scheme', 'http')}",
          "  title:", f"    en_US: {n.capitalize()}", f"    custom: {n.capitalize()}",
          "  category: MediaStack", '  hostname: ""']
    return "\n".join(L) + "\n"

out = pathlib.Path(__file__).parent / "apps"
for a in APPS:
    d = out / a["name"]; d.mkdir(parents=True, exist_ok=True)
    (d / "docker-compose.yml").write_text(render(a))
print(f"wrote {len(APPS)} apps to {out}")
