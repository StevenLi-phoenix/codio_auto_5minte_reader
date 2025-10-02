# Codio Course Reader Automation

## Overview

This project provides a minimal Selenium script that logs into Codio, scrapes the course dashboard, and automatically scrolls through each outstanding section. The tool ensures you stay on each page for more than 5 minutes, which may help with progress tracking, but it does **not** explicitly mark sections as read. 

**This is not an official tool from Codio.**
**Might violate the terms of service.**
**Use at your own risk.**
**It is not guaranteed to work.**
**You are responsible for your own actions.**
**It's not for you to cheating on reading time. It's for helping you to learn without manually scrolling.**

## Limitations

- **Currently only supports password login.**
- No warranty: the XPath selectors are extremely brittle and may break easily.

## Requirements

- Python 3.9 or newer
- Google Chrome installed locally
- ChromeDriver (handled automatically by recent Selenium releases via Selenium Manager)

Install Python dependencies:

```bash
pip install selenium python-dotenv tqdm
```

## Configuration

1. Create a `.env` file in the project root with your Codio credentials:
   ```env
   USERNAME="your_codio_email"
   PASSWORD="your_codio_password"
   ```

   Keep this file private; it contains plain-text credentials.
2. Optional: set `DISPLAY = True` in `main.py` if you want to watch the automated browser session.

## Usage

Run the automation from the repository root:

```bash
python main.py
```

The script performs the following steps:

- Launches Chrome and signs into Codio using the supplied credentials.
- Collects chapter and section metadata from the student dashboard.
- Writes a snapshot of the course contents and progress to `information.json`.
- Builds a work queue of sections that are not completed, disabled, answered, or labelled with “chip”.
- Opens each pending section, scrolls through the content for the configured duration, and returns to the dashboard.
- Records completed sections in `checkpoints.json` so they are skipped on subsequent runs.

The final `time.sleep(600)` keeps the session alive for ten minutes in case Codio performs background updates.

## Output Files

- `information.json`: Structured summary of every chapter and section the script observes.
- `checkpoints.json`: Rolling state used to avoid reopening sections already visited by the automation.

## Customization Tips

- Adjust `scroll_time` in `active_scroll` to change how long each section stays open.
- Replace the hard-coded `CODIO_URL` if your course path differs.
- Extend the filtering logic in the task builder if you need different skip conditions.

## Troubleshooting

- If Selenium cannot locate Chrome, ensure Chrome is in your PATH or install a compatible ChromeDriver manually.
- When selectors break after a Codio UI change, update the XPaths in `main.py` accordingly.
- Use `DISPLAY = True` to observe the browser when diagnosing failures.
