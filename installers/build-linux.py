#!/usr/bin/env python3
"""Linux: one tar.gz holding every staged plugin plus an install script.

    python3 installers/build-linux.py <suite version>     (after fetch.py linux-x64)
"""
import os, shutil, stat, sys, tarfile

here = os.path.dirname(os.path.abspath(__file__))
version = sys.argv[1]
stage = os.path.join(here, "build", "linux-x64", "stage")
name = f"Epsilon-Audio-Suite-{version}-linux-x64"
root = os.path.join(here, "build", "out", name)
shutil.rmtree(root, ignore_errors=True); os.makedirs(root)
for plugin in sorted(os.listdir(stage)):
    shutil.copytree(os.path.join(stage, plugin), os.path.join(root, "plugins", plugin), symlinks=True)

script = r'''#!/bin/sh
# Epsilon Audio Suite for Linux: installs the plugins you name (or all of them).
#   ./install.sh                     every plugin, for this user (~/.vst3, ~/.clap, ~/.vst)
#   ./install.sh Obsidian Mica       just those
#   sudo ./install.sh --system       every plugin, for all users (/usr/local/lib/vst3, clap, vst)
#   ./install.sh --uninstall [names] remove them again
set -e
cd "$(dirname "$0")/plugins"
mode=install; scope=user
for a in "$@"; do case "$a" in --system) scope=system;; --uninstall) mode=uninstall;; esac; done
if [ $scope = system ]; then vst3=/usr/local/lib/vst3; clap=/usr/local/lib/clap; vst=/usr/local/lib/vst
else vst3="$HOME/.vst3"; clap="$HOME/.clap"; vst="$HOME/.vst"; fi
names=""
for a in "$@"; do case "$a" in --*) ;; *) names="$names $a";; esac; done
[ -n "$names" ] || names="$(ls)"
mkdir -p "$vst3" "$clap" "$vst"
for n in $names; do
  [ -d "$n" ] || { echo "no plugin called $n (have: $(ls | tr '\n' ' '))"; exit 1; }
  if [ $mode = install ]; then
    rm -rf "$vst3/$n.vst3"; cp -R "$n/$n.vst3" "$vst3/"
    cp "$n/$n.clap" "$clap/"; cp "$n/$n-vst.so" "$vst/"
    echo "installed $n"
  else
    rm -rf "$vst3/$n.vst3" "$clap/$n.clap" "$vst/$n-vst.so"; echo "removed $n"
  fi
done
echo "Done. Rescan plugins in your DAW. Manuals: $(pwd)/<plugin>/<plugin>-Manual.html"
'''
path = os.path.join(root, "install.sh"); open(path, "w").write(script)
os.chmod(path, 0o755)
open(os.path.join(root, "README.txt"), "w").write(
    f"Epsilon Audio Suite {version} for Linux (x86_64)\n\nRun ./install.sh to install every plugin for your user,\n"
    "./install.sh Obsidian Mica to install some, or sudo ./install.sh --system for all users.\n"
    "./install.sh --uninstall removes them. Free and open source (MIT): https://plugins.epsilonrecords.com\n")
tgz = os.path.join(here, "build", "out", name + ".tar.gz")
with tarfile.open(tgz, "w:gz") as t: t.add(root, arcname=name)
shutil.rmtree(root)
print(tgz)
