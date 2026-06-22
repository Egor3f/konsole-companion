# konsole-companion

A daemon and GUI for KDE Konsole, driven over D-Bus.

- **Theme sync** — on a KDE light/dark switch, each session's profile swaps to its paired variant (e.g. *Black on White* for light, *Breeze* for dark).
- **Tab sets** — save named sets of tabs (path, name, profile) and restore them into the current window.

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

## Setup

Enable Konsole's D-Bus control once, in Settings → Configure Konsole → General →
*Enable the security sensitive parts of the DBus API*. Theme switching and tab
restore both need it.

Install the desktop entry and start the daemon:

```sh
install -Dm644 data/konsole-companion.desktop ~/.local/share/applications/
install -Dm644 data/konsole-companion-daemon.service ~/.config/systemd/user/
systemctl --user enable --now konsole-companion-daemon.service
```

## Configure theme pairs

Create two Konsole profiles (Settings → Manage Profiles → New) that differ only
in color scheme. Map them in `~/.config/konsole-companion/config.json`:

```json
{
  "pairs": [
    { "light": "Profile 1", "dark": "Profile 1 Dark" }
  ]
}
```

Names must match the profiles exactly.

## Run

| Command | Action |
|---|---|
| `konsole-companion` | open the tab-set manager |
| `konsole-companion-daemon` | run the theme watcher (the systemd unit does this) |

## Credits

Built by Egor3f together with Claude (Anthropic).

