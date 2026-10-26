#!/usr/bin/env python3
"""macOS: one installer package with a choice per plugin and, under it, per format.

    python3 installers/build-macos.py <suite version>     (after fetch.py macos-universal; runs on macOS)

Each plugin format becomes a component package installed to /Library/Audio/Plug-Ins/<format>; the manuals go
to /Library/Documentation/Epsilon Audio. productbuild joins them with a distribution file that lists every
plugin with its formats (VST3, AU and CLAP on; VST2 available but off).

Files the Installer writes are not quarantined, so the plugins load without any Terminal step even while the
package itself is unsigned. Signing and notarization run when these environment variables are set:
  MACOS_INSTALLER_IDENTITY   the "Developer ID Installer: ..." identity in the keychain (productsign)
  NOTARY_KEY_PATH, NOTARY_KEY_ID, NOTARY_ISSUER   an App Store Connect API key (notarytool)
Notarization also needs the plugins inside to be Developer ID signed with the hardened runtime, which each
plugin's own CI does once its signing secrets are set.
"""
import json, os, plistlib, shutil, subprocess, sys
from xml.sax.saxutils import escape

here = os.path.dirname(os.path.abspath(__file__))
version = sys.argv[1]
build = os.path.join(here, "build", "macos-universal")
stage = os.path.join(build, "stage")
work = os.path.join(build, "pkg"); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
outdir = os.path.join(here, "build", "out"); os.makedirs(outdir, exist_ok=True)
catalog = {p["name"]: p for p in json.load(open(os.path.join(here, "..", "plugins.json")))["plugins"]}
versions = {v["name"]: v["tag"] for v in json.load(open(os.path.join(build, "versions.json")))}
BID = "com.epsilonrecords.audio"

# (key, label, bundle suffix, Plug-Ins folder, selected by default)
FORMATS = [("vst3", "VST3", ".vst3", "VST3", True), ("au", "Audio Unit", ".component", "Components", True),
           ("clap", "CLAP", ".clap", "CLAP", True), ("vst2", "VST2", ".vst", "VST", False)]

def run(*cmd): print("+", " ".join(cmd)); subprocess.run(cmd, check=True)

def component(ident, root, pkg_version):
    """pkgbuild a payload root installed at /, with bundle relocation off (so an old copy elsewhere is not 'upgraded')."""
    plist = os.path.join(work, ident + ".plist")
    run("pkgbuild", "--analyze", "--root", root, plist)
    entries = plistlib.load(open(plist, "rb"))
    for e in entries: e["BundleIsRelocatable"] = False; e["BundleOverwriteAction"] = "upgrade"
    plistlib.dump(entries, open(plist, "wb"))
    pkg = os.path.join(work, ident + ".pkg")
    run("pkgbuild", "--root", root, "--component-plist", plist, "--identifier", f"{BID}.{ident}",
        "--version", pkg_version, "--install-location", "/", pkg)
    return os.path.basename(pkg)

choices, lines = [], []
for name in sorted(stage_names := os.listdir(stage), key=lambda n: list(catalog).index(n) if n in catalog else 99):
    src = os.path.join(stage, name); tag = versions.get(name, "").lstrip("v") or "0"
    subs = []
    for key, label, suffix, folder, on in FORMATS:
        bundle = os.path.join(src, name + suffix)
        if not os.path.exists(bundle): continue
        root = os.path.join(work, "roots", f"{name}-{key}", "Library", "Audio", "Plug-Ins", folder)
        os.makedirs(root)
        run("ditto", bundle, os.path.join(root, name + suffix))
        pkg = component(f"{name.lower()}.{key}", os.path.join(work, "roots", f"{name}-{key}"), tag)
        subs.append((key, label, on, pkg))
    manual = os.path.join(src, f"{name}-Manual.html")
    if os.path.exists(manual):
        root = os.path.join(work, "roots", f"{name}-manual", "Library", "Documentation", "Epsilon Audio")
        os.makedirs(root); shutil.copy(manual, root)
        subs.append(("manual", "Manual", True, component(f"{name.lower()}.manual", os.path.join(work, "roots", f"{name}-manual"), tag)))
    summary = catalog.get(name, {}).get("summary", "")
    lines.append(f'    <line choice="{name.lower()}">' + "".join(f'<line choice="{name.lower()}.{k}"/>' for k, _, _, _ in subs) + "</line>")
    choices.append(f'  <choice id="{name.lower()}" title="{escape(name)} {escape(tag)}" description="{escape(summary)}"/>')
    for k, label, on, pkg in subs:
        choices.append(f'  <choice id="{name.lower()}.{k}" title="{label}" start_selected="{"true" if on else "false"}">'
                       f'<pkg-ref id="{BID}.{name.lower()}.{k}"/></choice>')
        choices.append(f'  <pkg-ref id="{BID}.{name.lower()}.{k}" version="{tag}" onConclusion="none">{pkg}</pkg-ref>')

res = os.path.join(work, "resources"); os.makedirs(res)
open(os.path.join(res, "welcome.html"), "w").write(f"""<html><body style="font-family:-apple-system,Helvetica;font-size:13px">
<h2>Epsilon Audio Suite {escape(version)}</h2>
<p>Fifteen free, open-source instruments and effects from Epsilon Records.</p>
<p>On the next pages you can choose which plugins and formats to install. VST3, Audio Unit and CLAP are selected;
VST2 is available for older hosts. Plugins go to /Library/Audio/Plug-Ins, manuals to /Library/Documentation/Epsilon Audio.</p>
<p>After installing, rescan plugins in your DAW. Guides: <a href="https://plugins.epsilonrecords.com/install">plugins.epsilonrecords.com/install</a></p>
</body></html>""")
shutil.copy(os.path.join(here, "..", "LICENSE"), os.path.join(res, "license.txt"))
dist = f"""<?xml version="1.0" encoding="utf-8"?>
<installer-gui-script minSpecVersion="2">
  <title>Epsilon Audio Suite {escape(version)}</title>
  <organization>{BID}</organization>
  <welcome file="welcome.html" mime-type="text/html"/>
  <license file="license.txt" mime-type="text/plain"/>
  <options customize="always" require-scripts="false" hostArchitectures="arm64,x86_64"/>
  <domains enable_localSystem="true"/>
  <volume-check><allowed-os-versions><os-version min="10.13"/></allowed-os-versions></volume-check>
  <choices-outline>
{chr(10).join(lines)}
  </choices-outline>
{chr(10).join(choices)}
</installer-gui-script>
"""
dpath = os.path.join(work, "distribution.xml"); open(dpath, "w").write(dist)
base = f"Epsilon-Audio-Suite-{version}-macos"
unsigned = os.path.join(work, base + "-unsigned.pkg")
run("productbuild", "--distribution", dpath, "--resources", res, "--package-path", work, unsigned)
final = os.path.join(outdir, base + ".pkg")
ident = os.environ.get("MACOS_INSTALLER_IDENTITY")
if ident:
    run("productsign", "--sign", ident, "--timestamp", unsigned, final)
    if os.environ.get("NOTARY_KEY_PATH"):
        run("xcrun", "notarytool", "submit", final, "--key", os.environ["NOTARY_KEY_PATH"], "--key-id",
            os.environ["NOTARY_KEY_ID"], "--issuer", os.environ["NOTARY_ISSUER"], "--wait")
        run("xcrun", "stapler", "staple", final)
else:
    print("::warning::MACOS_INSTALLER_IDENTITY not set: the package is unsigned (open it with right-click > Open, "
          "or System Settings > Privacy & Security > Open Anyway)")
    shutil.copy(unsigned, final)
print(final)
