# -*- coding: utf-8 -*-
import os
import zipfile
import tempfile

import requests
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

ADDON = xbmcaddon.Addon()
REPO_OWNER = "aco730"
REPO_NAME = "kodi-clone-backup"
API_BASE = "https://api.github.com/repos/{0}/{1}".format(REPO_OWNER, REPO_NAME)

ADDONS_DIR = xbmcvfs.translatePath("special://home/addons/")
USERDATA_DIR = xbmcvfs.translatePath("special://userdata/")

# (checkbox label, kind, path-in-repo or addon id list)
CATALOG = [
    ("Setarile mele personale (guisettings, credentiale, cookie-uri)", "userdata", "userdata-backup.zip"),
    ("DigiOnline.ro", "addon", "repository/addons/plugin.video.DigiOnline.ro/plugin.video.DigiOnline.ro-1.0.1.zip"),
    ("Stiri RSS", "addon", "repository/addons/plugin.program.newsreader/plugin.program.newsreader-1.0.0.zip"),
    ("Weather (Gismeteo) + dependinte", "addon_multi", [
        "repository/addons/script.module.future/script.module.future-1.0.0+matrix.1.zip",
        "repository/addons/script.module.simpleplugin3/script.module.simpleplugin3-3.0.6+matrix.1.zip",
        "repository/addons/weather.gismeteo/weather.gismeteo-0.6.4+matrix.1.zip",
    ]),
    ("Skin Confluence (varianta mea, meniu/fundal custom)", "addon", "repository/addons/skin.confluence/skin.confluence-5.0.9.1.zip"),
    ("TheCrew + Cumination + MadTitanSports + POV (live, auto-update real)", "thecrew", None),
]


def get_token():
    token = ADDON.getSetting("github_token")
    if token:
        return token
    dialog = xbmcgui.Dialog()
    token = dialog.input("GitHub token (repo privat, o singura data)", type=xbmcgui.INPUT_ALPHANUM)
    if not token:
        return None
    ADDON.setSetting("github_token", token)
    return token


def gh_headers(token):
    return {"Authorization": "token " + token, "Accept": "application/vnd.github.v3+json"}


def fetch_repo_file_bytes(token, path_in_repo):
    # Step 1: get the blob sha for this path (works for any file size).
    meta_url = "{0}/contents/{1}".format(API_BASE, path_in_repo)
    r = requests.get(meta_url, headers=gh_headers(token), timeout=30)
    if r.status_code != 200:
        raise Exception("{0}: {1}".format(r.status_code, r.text[:200]))
    sha = r.json()["sha"]

    # Step 2: fetch the raw blob content directly (handles files > 1MB too).
    blob_url = "{0}/git/blobs/{1}".format(API_BASE, sha)
    headers = gh_headers(token)
    headers["Accept"] = "application/vnd.github.raw"
    r2 = requests.get(blob_url, headers=headers, timeout=60)
    if r2.status_code != 200:
        raise Exception("blob {0}: {1}".format(r2.status_code, r2.text[:200]))
    return r2.content


def extract_zip_bytes(zip_bytes, dest_dir):
    tmp_zip = os.path.join(tempfile.gettempdir(), "aco730_dl.zip")
    with open(tmp_zip, "wb") as f:
        f.write(zip_bytes)
    with zipfile.ZipFile(tmp_zip, "r") as zf:
        zf.extractall(dest_dir)
    os.remove(tmp_zip)


def install_addon_zip(token, path_in_repo, progress, label):
    progress.update(progress.getPercent(), "Descarc: " + label)
    data = fetch_repo_file_bytes(token, path_in_repo)
    extract_zip_bytes(data, ADDONS_DIR)


def restore_userdata(token, progress):
    progress.update(progress.getPercent(), "Descarc setarile personale...")
    data = fetch_repo_file_bytes(token, "userdata-backup.zip")
    extract_zip_bytes(data, USERDATA_DIR)


def install_thecrew_bundle(token, progress):
    progress.update(progress.getPercent(), "Descarc repository.thecrew...")
    data = fetch_repo_file_bytes(token, "repository/addons/repository.thecrew/repository.thecrew-0.3.8.zip")
    extract_zip_bytes(data, ADDONS_DIR)
    xbmc.executebuiltin("UpdateLocalAddons")
    xbmc.sleep(1500)
    for addon_id in ("plugin.video.thecrew", "plugin.video.cumination",
                      "plugin.video.madtitansports", "plugin.video.pov"):
        progress.update(progress.getPercent(), "Instalez: " + addon_id)
        xbmc.executebuiltin("InstallAddon({0})".format(addon_id))
        xbmc.sleep(2500)


def main():
    dialog = xbmcgui.Dialog()
    labels = [c[0] for c in CATALOG]
    selected = dialog.multiselect("aco730 - Setup Wizard (bifeaza ce vrei instalat)", labels, preselect=list(range(len(labels))))
    if not selected:
        return

    token = get_token()
    if not token:
        dialog.notification("Setup Wizard", "Anulat (fara token)", xbmcgui.NOTIFICATION_WARNING, 3000)
        return

    progress = xbmcgui.DialogProgress()
    progress.create("aco730 - Setup Wizard", "Pornesc...")

    errors = []
    total = len(selected)
    for i, idx in enumerate(selected):
        if progress.iscanceled():
            break
        label, kind, ref = CATALOG[idx]
        pct = int((i / float(total)) * 100)
        progress.update(pct, label)
        try:
            if kind == "userdata":
                restore_userdata(token, progress)
            elif kind == "addon":
                install_addon_zip(token, ref, progress, label)
            elif kind == "addon_multi":
                for p in ref:
                    install_addon_zip(token, p, progress, label)
            elif kind == "thecrew":
                install_thecrew_bundle(token, progress)
        except Exception as e:
            errors.append("{0}: {1}".format(label, e))

    progress.update(100, "Gata")
    progress.close()

    xbmc.executebuiltin("UpdateLocalAddons")

    if errors:
        dialog.ok("Setup Wizard - erori", "\n".join(errors))
    else:
        dialog.ok(
            "aco730 - Setup Wizard",
            "Gata! Restarteaza Kodi acum ca totul sa se aplice complet "
            "(skin, addon-uri, setari).",
        )
    xbmc.log("aco730restore: wizard run finished, errors=" + str(errors), xbmc.LOGINFO)


if __name__ == "__main__":
    main()
