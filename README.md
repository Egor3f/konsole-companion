# konsole-companion

A GUI and a background daemon for KDE Konsole, driven over D-Bus.

- **Tab sets** — save named sets of tabs (path, name, profile, color) and restore them into the current window.
- **Tab guard** — a daemon that reapplies each tab's name and color after Konsole switches profiles on a system light/dark change, which otherwise clears them.

## Requirements

- KDE Konsole
- Python ≥ 3.10
- PySide6 from your distribution's package manager

PySide6 ships compiled Qt plugins, so use the distro package, not the PyPI wheel.

## Install

Install the dependencies:

| Distro | Command |
|---|---|
| Arch / Manjaro / CachyOS | `sudo pacman -S pyside6 python-pipx` |
| Fedora | `sudo dnf install python3-pyside6 pipx` |
| Debian / Ubuntu | `sudo apt install python3-pyside6.qtwidgets python3-pyside6.qtdbus pipx` |
| openSUSE | `sudo zypper install python3-PySide6 python3-pipx` |

Install the app so its virtualenv reuses the system PySide6:

```sh
git clone https://github.com/egor3f/konsole-companion
cd konsole-companion
pipx install --system-site-packages .
```

Install the desktop entry and start the tab guard:

```sh
install -Dm644 data/konsole-companion.desktop ~/.local/share/applications/
install -Dm644 data/konsole-companion-daemon.service ~/.config/systemd/user/
systemctl --user enable --now konsole-companion-daemon.service
```

## Setup

Enable Konsole's D-Bus control once, in Settings → Configure Konsole → General →
*Enable the security sensitive parts of the DBus API*. Tab restore needs it.

## Run

| Command | Action |
|---|---|
| `konsole-companion` | open the tab-set manager |
| `konsole-companion-daemon` | run the tab guard (the systemd unit does this) |

## Credits

Built by Egor3f together with Claude (Anthropic).
