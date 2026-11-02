#!/usr/bin/env bash

set -e

REPO_RAW="https://raw.githubusercontent.com/YOUR_USERNAME/nullmatrix/main/nullmatrix.py"
BIN_DIR="$HOME/.local/bin"
TARGET="$BIN_DIR/nullmatrix"
MARKER="# added by nullmatrix installer"

say() { printf '%s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

if [ "$1" = "--uninstall" ]; then
    rm -f "$TARGET"
    say "removed $TARGET"
    say "(the PATH line in your shell config is harmless; delete it by hand if you want)"
    exit 0
fi

command -v python3 >/dev/null 2>&1 || die "python3 not found. Install Python 3 first."

python3 -c "import curses" >/dev/null 2>&1 \
    || die "Python's curses module is missing. On Debian/Ubuntu try: sudo apt install python3-dev (or reinstall python3)."

mkdir -p "$BIN_DIR"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || echo "")"

if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/nullmatrix.py" ]; then
    cp "$SCRIPT_DIR/nullmatrix.py" "$TARGET"
else
    say "nullmatrix.py not found next to installer, downloading..."
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$REPO_RAW" -o "$TARGET" || die "download failed"
    elif command -v wget >/dev/null 2>&1; then
        wget -q "$REPO_RAW" -O "$TARGET" || die "download failed"
    else
        die "need curl or wget to download nullmatrix.py"
    fi
fi

chmod +x "$TARGET"
say "installed to $TARGET"

case ":$PATH:" in
    *":$BIN_DIR:"*)
        say "$BIN_DIR is already on your PATH"
        NEED_RELOAD=0
        ;;
    *)
        NEED_RELOAD=1
        add_line() {
            rc="$1"; line="$2"
            touch "$rc"
            if ! grep -qF "$MARKER" "$rc" 2>/dev/null; then
                printf '\n%s\n%s\n' "$MARKER" "$line" >> "$rc"
                say "added $BIN_DIR to PATH in $rc"
            fi
        }

        LINE='export PATH="$HOME/.local/bin:$PATH"'
        user_shell="$(basename "${SHELL:-}")"

        case "$user_shell" in
            zsh)  add_line "$HOME/.zshrc" "$LINE" ;;
            fish)
                mkdir -p "$HOME/.config/fish"
                add_line "$HOME/.config/fish/config.fish" 'fish_add_path $HOME/.local/bin'
                ;;
            *)
                add_line "$HOME/.bashrc" "$LINE"
                [ -f "$HOME/.bash_profile" ] && add_line "$HOME/.bash_profile" "$LINE"
                [ -f "$HOME/.profile" ] && add_line "$HOME/.profile" "$LINE"
                ;;
        esac
        ;;
esac

say ""
say "done! "
if [ "$NEED_RELOAD" = "1" ]; then
    say "open a NEW terminal (or run: source ~/.${user_shell:-bash}rc) and type:  nullmatrix"
else
    say "type:  nullmatrix"
fi
