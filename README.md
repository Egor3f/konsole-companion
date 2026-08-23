# konsole-companion

A GUI for saving and restoring sets of KDE Konsole tabs, driven over D-Bus.

Save named sets of tabs (path, name, profile, color) and restore them into the current window.

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

Install the desktop entry:

```sh
install -Dm644 data/konsole-companion.desktop ~/.local/share/applications/
```

## Setup

Enable Konsole's D-Bus control once, in Settings → Configure Konsole → General →
*Enable the security sensitive parts of the DBus API*. Tab restore needs it.

## Run

Launch `konsole-companion` to open the tab-set manager.

## Credits

Built by Egor3f together with Claude (Anthropic).
