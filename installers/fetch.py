#!/usr/bin/env python3
"""Download the latest release zip of every plugin in plugins.json for one platform, check it against the
release's SHA256SUMS.txt when the release has one, and unpack it into build/<platform>/stage/<Plugin>/.

    python3 installers/fetch.py <macos-universal|windows-x64|linux-x64>

Uses the GitHub REST API (a token in GH_TOKEN or GITHUB_TOKEN raises the rate limit). Writes
build/<platform>/versions.json with each plugin's tag, for the installer's version string and notes.
"""
import hashlib, json, os, shutil, sys, urllib.request, zipfile

here = os.path.dirname(os.path.abspath(__file__))
platform = sys.argv[1]
out = os.path.join(here, "build", platform)
shutil.rmtree(out, ignore_errors=True)
os.makedirs(os.path.join(out, "zips")); os.makedirs(os.path.join(out, "stage"))
token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

def get(url, accept="application/vnd.github+json"):
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "epsilon-installers"})
    if token: req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as r: return r.read()

catalog = json.load(open(os.path.join(here, "..", "plugins.json")))
versions = []
for p in catalog["plugins"]:
    name = p["name"]; repo = p["repo"].rstrip("/").split("github.com/")[1]
    rel = json.loads(get(f"https://api.github.com/repos/{repo}/releases/latest"))
    assets = {a["name"]: a for a in rel["assets"]}
    zname = f"{name}-{platform}.zip"
    if zname not in assets: sys.exit(f"{name} {rel['tag_name']}: no {zname}")
    data = get(assets[zname]["url"], "application/octet-stream")
    zpath = os.path.join(out, "zips", zname); open(zpath, "wb").write(data)
    digest = hashlib.sha256(data).hexdigest()
    if "SHA256SUMS.txt" in assets:
        sums = get(assets["SHA256SUMS.txt"]["url"], "application/octet-stream").decode()
        want = {l.split()[1].lstrip("*"): l.split()[0] for l in sums.splitlines() if l.strip()}
        if want.get(zname) != digest: sys.exit(f"checksum mismatch for {zname}")
        check = "verified"
    else:
        check = "no SHA256SUMS.txt in this release"
        print(f"::warning::{name} {rel['tag_name']}: {check}")
    dest = os.path.join(out, "stage", name)
    with zipfile.ZipFile(zpath) as z: z.extractall(dest)
    inner = os.path.join(dest, platform)          # the zips hold one folder named after the platform
    if os.path.isdir(inner):
        for f in os.listdir(inner): shutil.move(os.path.join(inner, f), dest)
        os.rmdir(inner)
    # zipfile drops Unix permissions; restore the executable bit on bundle binaries
    for root, _, files in os.walk(dest):
        for f in files:
            if "/MacOS" in root or f.endswith((".so", ".clap")): os.chmod(os.path.join(root, f), 0o755)
    versions.append({"name": name, "tag": rel["tag_name"], "sha256": digest, "check": check})
    print(f"{name:10} {rel['tag_name']:8} {check}")
json.dump(versions, open(os.path.join(out, "versions.json"), "w"), indent=1)
print(f"staged {len(versions)} plugins in {out}/stage")
