# File Organizer Pro

A desktop file management and safe quarantine utility built with Python and Tkinter.

## Features

- **Config-Driven:** Loads file categories, extensions, and rules from an external `config.json` file.
- **Dual Undo Controls:** Independent buttons to instantly revert recent organize or cleanup actions.
- **Safe Quarantine:** Isolates temporary and junk files into a quarantine folder instead of permanent deletion.
- **Automated Deployment:** Automatically drops a desktop shortcut (`.lnk`) on first run using `winshell`.
- **Activity Logging:** Tracks events and timestamps in a local `app.log` file.
- **Dark-Slate GUI:** Clean, modern interface designed for local utility tasks.

## Requirements

- Python 3.x
- Dependencies:
  ```bash
  pip install winshell pywin32
