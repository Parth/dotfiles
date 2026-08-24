#!/bin/sh
set -eu

say() { echo "==> $*" >&2; }

here=$(dirname "$0")
version=${1:-$(sed -n 's/.*minimum_zig_version = "\([^"]*\)".*/\1/p' "$here/build.zig.zon")}
prefix=${ZIG_PREFIX:-$HOME/.local}

case $(uname -s) in
    Darwin) os=macos ;;
    MINGW*|MSYS*|CYGWIN*) os=windows ;;
    *) os=$(uname -s | tr 'A-Z' 'a-z') ;;
esac

case $(uname -m) in
    amd64) arch=x86_64 ;;
    arm64) arch=aarch64 ;;
    armv*) arch=arm ;;
    i?86) arch=x86 ;;
    ppc64le) arch=powerpc64le ;;
    *) arch=$(uname -m) ;;
esac

dest=$prefix/share/zig/$version
say "zig $version for $arch-$os"

if [ -x "$dest/zig" ]; then
    say "already unpacked at $dest"
else
    url=https://ziglang.org/download/$version/zig-$arch-$os-$version.tar.xz
    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT
    say "fetching and unpacking $url"
    if command -v curl >/dev/null 2>&1; then
        curl -fL --progress-bar "$url"
    else
        wget -O- "$url"
    fi | tar -xf - -C "$tmp"
    set -- "$tmp"/zig-*/zig
    [ -x "$1" ] || { say "failed: nothing usable came back from $url"; exit 1; }
    say "installing to $dest"
    mkdir -p "$prefix/share/zig"
    mv "${1%/zig}" "$dest"
fi

mkdir -p "$prefix/bin"
ln -sf "$dest/zig" "$prefix/bin/zig"
say "$prefix/bin/zig is now $("$dest/zig" version)"

case ":$PATH:" in
    *":$prefix/bin:"*) ;;
    *) say "note: $prefix/bin is not on your PATH" ;;
esac
