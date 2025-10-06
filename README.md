# PetWALK Home Assistant Custom Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
![Version](https://img.shields.io/github/v/release/YOUR_USERNAME/hapetwalk)

Local REST API control for PetWALK smart doors.

## Installation (HACS – recommended)
1. Add this repo to HACS (Settings → Repositories → Custom repositories)
2. Install “PetWALK”
3. Restart HA
4. Settings → Devices & Services → Add Integration → PetWALK

## Manual Installation
Copy `custom_components/petwalk/` to your `/config/custom_components/` folder and restart HA.

## Configuration
- IP address (same as app)
- Username / Password (same as app)
- Port (default 8080)
- Flag “Include all door events” to create pet sensors/trackers

## Changelog
See [CHANGELOG.md](CHANGELOG.md)