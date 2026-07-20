```
            .--~~,__
:-....,-------`~~'._.'
`-,,,  ,_      ;'~U'
 _,-' ,'`-__; '--.
(_/'~~      ''''(;
```
# Woofie Postman I2P Magnet Fetcher

Woofie is a command-line tool that behaves like a CLI browser for Postman - downloads each page, gets magnet links, allows user to select which ones they want.
**It is not an invasive, agressive crawler, but a Lynx-esq friendly Postman interface. It behaves exactly like a browser would.**

The script was made for a better Postman experience. Please do not abuse it and be careful what you're downloading.

## Principles

- Minimal dependencies (`requests`, `pyfiglet` only)
- Maximum modifiability (user can change all options)
- Direct integration with i2psnark via HTTP POST
- Safety filters for caution

## Features

- Fetches and displays torrents from Postman tracker with page navigation
- Interactive magnet selection 
- Not-wanted magnet filtering (skip previously rejected magnets across runs)
- Automatic nonce extraction and POST to i2psnark web interface
- Color-coded terminal output for readability
- Saves settings to `config.json` for reuse across runs
- Modify settings on every run (even when config exists)
- Danger filter with customizable filtered words
- Copyright filter to block known copyrighted content
- Disk space allocation: set a max total size, torrents are skipped when the limit would be exceeded

## Requirements

- Python 3.x
- `requests` (`pip install requests`)
- `pyfiglet` (`pip install pyfiglet`)
- Running I2P router with HTTP proxy (default is `127.0.0.1:4444`)
- Running i2psnark instance (default is `http://127.0.0.1:7657/i2psnark/`)

## Usage
**On Linux, preferably make a virtual environment using:**
```bash
python3 -m venv venv
source venv/bin/activate
```
```bash
pip install requests pyfiglet
python program.py
```

## How it works

1. Connects to Postman tracker via I2P HTTP proxy
2. Fetches landing page, extracts form token
3. Authenticates session with tracker
4. Parses torrent listing pages, displays magnet links with size and peer info
5. Applies filters: danger words, copyright keywords, seeders (skips 0-seeder torrents), disk space limit
6. User selects/deselects magnets interactively
7. Selected magnets are saved to `selected_magnets.txt`
8. Program connects to local i2psnark, extracts nonce
9. Each magnet is POSTed to `/_post` with `action=Add`

## Configuration

On first run, the program asks for your settings and offers to save them to `config.json`. On subsequent runs, saved settings are loaded automatically. You can choose to modify settings at any time.

Defaults:
- **Router type:** Official (port 7657) or standalone (port 8002)
- **Tracker URL:** `http://tracker2.postman.i2p/`
- **Proxy:** `127.0.0.1:4444`
- **i2psnark URL:** `http://127.0.0.1:7657/i2psnark/` (official) or `http://127.0.0.1:8002/i2psnark/` (standalone)
- **Danger filter:** Disabled by default
- **Copyright filter:** Disabled by default
- **Disk space limit:** Disabled by default (set max total GB when enabled)

## Danger Filter

The danger filter blocks torrents with certain keywords in their titles (e.g. "guns", "explosives", "drugs"). Customize by editing `danger_words.txt` (one word per line).

## Copyright Filter

The copyright filter blocks torrents containing known copyrighted material names in their titles (e.g. "marvel", "disney", "netflix"). This is keyword-based, not an API lookup, so it only catches explicit matches. Customize by editing `copyright_words.txt` (one word per line).

## Files

| File | Description |
|------|-------------|
| `program.py` | Main script |
| `config.json` | Saved settings (created on first run) |
| `danger_words.txt` | Custom danger filter words |
| `copyright_words.txt` | Custom copyright filter words |
| `selected_magnets.txt` | Selected magnet links ready to add |
| `not_wanted_magnets.txt` | Rejected magnets (persisted across runs) |

## Author

Started by C0m3b4ck on July 18th, 2026, under APL 2.0
