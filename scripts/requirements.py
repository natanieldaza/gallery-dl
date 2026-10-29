#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

import util
import sys
import re
import argparse
import requests

REQUIREMENTS = {}
session = None
results = {}


def package_hashes(pkg, args):
    global session
    if session is None:
        session = requests.Session()

    pkg, eq, version = pkg.partition("==")
    if pkg in REQUIREMENTS:
        u = f"https://pypi.org/pypi/{pkg}/{REQUIREMENTS[pkg]}/json"
    elif version:
        u = f"https://pypi.org/pypi/{pkg}/{version}/json"
    else:
        u = f"https://pypi.org/pypi/{pkg}/json"

    d = session.get(u).json()
    if not (i := d.get("info")):
        return

    n = i["name"]
    results[n.lower()] = result = {
        "name"   : n,
        "version": i["version"],
        "files"  : [],
        "dependencies": [],
        "extras" : {},
        "parents": [],
    }

    def append(file):
        files.append(((file["filename"], file["digests"]["sha256"])))

    py3 = None
    files = result["files"]
    wheels = {v: (0, ()) for v in args.versions}

    for u in d["urls"]:
        if u.get("yanked"):
            continue
        if not args.sdist and u["packagetype"] == "sdist":
            continue

        v = u["python_version"]
        n = u["filename"]
        if v in {"py3", "py2.py3"} and "py3-none-any." in n:
            py3 = u
            continue

        if args.freethreaded and args.freethreaded(n):
            continue
        if args.architecture and not args.architecture(n):
            continue
        if args.platform and not args.platform(n):
            continue

        if v in args.python:
            wheels[99] = (99, ())
        elif v.startswith("cp3"):
            if f"-{v}t-" in n:
                continue
            v = int(v[3:])
            for version, (current, fs) in wheels.items():
                if v > version:
                    continue
                if v > current:
                    wheels[version] = (v, [u])
                elif v == current:
                    fs.append(u)
            continue
        else:
            continue

        append(u)

    if not files and wheels:
        for _, fs in wheels.values():
            for u in fs:
                append(u)
    if not files and py3:
        append(py3)

    for d in i["requires_dist"] or ():
        name = re.sub(r"([\w-]+).*", r"\1", d).lower()

        pos = d.find(" extra == ")
        if pos < 0:
            result["dependencies"].append(name)
        else:
            extra = d[pos+11:d.find('"', pos+11)]
            if e := result["extras"].get(extra):
                e.append(name)
            else:
                result["extras"][extra] = [name]

    return result


def collect(pkg, args, level=0, parent=None):
    pkg = pkg.replace("_", "-")
    pkgl = pkg.partition("==")[0].lower()
    pkgl, ex, extras = pkgl.partition("[")
    if pkgl in args.exclude:
        return
    if pkgl not in results:
        if ex:
            pkg = pkg.partition("[")[0]
        results[pkgl] = info = package_hashes(pkg, args)

        if args.dependencies > level:
            for dep in info["dependencies"]:
                collect(dep, args, level+1, pkg)

        if not level:
            if ex:
                extras = (extras[:-1],)
            else:
                extras = info["extras"] if args.Extra else args.extra
            for extra in extras:
                for dep in info["extras"][extra]:
                    collect(dep, args, level+1, f"{pkgl}[{extra}]")
    if parent:
        results[pkgl]["parents"].append(parent)


def output(write, args):
    pkgs = list(results.values())
    pkgs.sort(key=lambda p: (
        bool(p["parents"]), len(p["files"]), p["name"].lower()))

    first = True
    for pkg in pkgs:
        if pkg["files"]:
            if first:
                first = False
            else:
                write("\n")

            write(f'{pkg["name"]}=={pkg["version"]} \\\n')
            for name, sha256 in pkg["files"]:
                write(f'    --hash=sha256:{sha256} \\\n')
            if args.filenames:
                for name, sha256 in pkg["files"]:
                    write(f'    # {name} \\\n')
            if pkg["parents"]:
                parents = sorted(set(pkg["parents"]))
                write(f'    # from {", ".join(parents)}\n')


def update(args):
    if target := args.update:
        targets = (("", "pyinstaller", "secretstorage")
                   if target == "all" else (target,))
    else:
        targets = ("",)

    write = sys.stdout.write
    for target in targets:
        if target and target[0] != "_":
            target = "_" + target
        path = "./requirements/versions" + target
        write(f"Updating '{path}'\n")
        path = util.path(path)
        with open(path) as fp:
            lines = fp.readlines()

        session = requests.Session()
        for idx, line in enumerate(lines):
            line = line.strip()
            if not line or line[0] == "#":
                continue
            pkg, _, version = line.partition("==")
            u = f"https://pypi.org/pypi/{pkg}/json"
            d = session.get(u).json()
            if not (i := d.get("info")):
                continue
            if version != i["version"]:
                write(f"- {i['name']}: {version} >> {i['version']}\n")
            lines[idx] = f"{i['name']}=={i['version']}\n"

        with open(path, "w") as fp:
            fp.writelines(lines)


def parse_args(args=None):
    parser = argparse.ArgumentParser(args)
    parser.add_argument("-a", "--architecture", action="append", default=[])
    parser.add_argument("-d", "--dependencies", action="count", default=0)
    parser.add_argument("-D", "--Dependencies",
                        dest="dependencies", action="store_const", const=128)
    parser.add_argument("-e", "--extra", action="append", default=[])
    parser.add_argument("-E", "--Extra", action="store_true")
    parser.add_argument("-f", "--freethreaded", action="store_true")
    parser.add_argument("-F", "--filenames", action="store_true")
    parser.add_argument("-i", "--input", action="append")
    parser.add_argument("-N", "--no-clobber", default="w",
                        dest="mode", action="store_const", const="x")
    parser.add_argument("-o", "--output")
    parser.add_argument("-O", "--Output")
    parser.add_argument("-p", "--platform", action="append", default=[])
    parser.add_argument("-P", "--python", action="append", default=[])
    parser.add_argument("-s", "--sdist", action="store_true")
    parser.add_argument("-u", "--update", const="", nargs="?")
    parser.add_argument("-x", "--exclude", action="append", default=[])

    parser.add_argument("--x32", "--x86", action="store_true")
    parser.add_argument("--x64", "--x86_64", "--x86-64", "--amd64",
                        action="store_true")
    parser.add_argument("--arm64", action="store_true")

    parser.add_argument("--windows", action="store_true")
    parser.add_argument("--linux", action="store_true")
    parser.add_argument("--manylinux", "--glibc", action="store_true")
    parser.add_argument("--musllinux", action="store_true")
    parser.add_argument("--macosx", "--osx", action="store_true")

    for v in map(str, range(8, 15)):
        parser.add_argument("--py" + v, dest="python",
                            action="append_const", const="cp3" + v)

    parser.add_argument("PKGS", nargs="*")
    args = parser.parse_args()
    pkgs = args.pkgs = args.PKGS

    if args.input:
        for path in args.input:
            with util.open(path) as fp:
                for line in fp:
                    line = line.strip()
                    if not line or line[0] == "#":
                        continue
                    pkgs.append(line)

    if args.Output:
        if not args.pkgs:
            args.pkgs = (args.Output,)
        args.output = util.path("requirements", args.Output.lower())

    if args.freethreaded:
        args.freethreaded = False
    else:
        args.freethreaded = re.compile(
            r"p\d+t-").search

    if args.x32:
        args.architecture.append("win32")
    if args.x64:
        args.architecture.append("(?:x86_|amd)64")
    if args.arm64:
        args.architecture.append("universal2")
        args.architecture.append("a(?:arch|rm)64")
    if args.architecture:
        args.architecture = re.compile(
            fr"_(?:{'|'.join(args.architecture)})\.").search

    if args.windows:
        args.platform.append("win")
    if args.linux:
        args.manylinux = args.musllinux = True
    if args.manylinux:
        args.platform.append("manylinux\\d*")
    if args.musllinux:
        args.platform.append("musllinux")
    if args.macosx:
        args.platform.append("macosx")
    if args.platform:
        args.platform = re.compile(
            fr"-(?:{'|'.join(args.platform)})_").search

    if args.python:
        for i, p in enumerate(args.python):
            if p.isdecimal():
                args.python[i] = f"cp3{p}"
        args.versions = [int(p[3:]) for p in args.python]
    else:
        args.python.append("cp314")
        args.versions = [14]
    args.python.append("py3")

    return args


def main():
    args = parse_args()

    if args.update is not None:
        update(args)
    if args.pkgs:
        for pkg in args.pkgs:
            pkg, eq, version = pkg.partition("==")
            if eq:
                REQUIREMENTS[pkg] = version
        for pkg in args.pkgs:
            collect(pkg, args)

    if not args.output or args.output == "-":
        output(sys.stdout.write, args)
    else:
        with util.lazy(args.output, args.mode) as fp:
            output(fp.write, args)


if __name__ == "__main__":
    main()
