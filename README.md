# Camoufox add_init_script Temporary Workaround
A temporary workaround solution for injecting JavaScript code at page initialization since `page.add_init_script()` doesn't work:

> In Camoufox, all of Playwright's JavaScript runs in an isolated context. This prevents Playwright from running JavaScript that writes to the main world/context of the page.
>
> While this is helpful with preventing detection of the Playwright page agent, it causes some issues with native Playwright functions like setting file inputs, executing JavaScript, adding page init scripts, etc. These features might need to be implemented separately.
>
> A current workaround for this might be to create a small dummy addon to inject into the browser.

*Source: [Camoufox Issue #48](https://github.com/daijro/camoufox/issues/48#issuecomment-2441091593)*

## Overview
This project uses a small browser extension to inject JavaScript code into pages at the earliest possible moment (`document_start`).

## Installation
```bash
pip install -r requirements.txt
```

## Usage

*See [example.py](example.py) for a real working example*


```python
import asyncio
import os

from camoufox import AsyncCamoufox

from add_init_script import add_init_script

# path to the addon directory, relative to the script location (default 'addon')
ADDON_PATH = 'addon'


async def main():
    # script that has to load before page does
    script = '''
    console.log('Demo script injected at page start');
    '''

    async with AsyncCamoufox(
            headless=True,
            main_world_eval=True,  # 1. add this to enable main world evaluation
            addons=[os.path.abspath(ADDON_PATH)]  # 2. add this to load the addon that will inject the scripts on init
    ) as browser:
        page = await browser.new_page()

        # use add_init_script() instead of page.add_init_script()
        await add_init_script(script, ADDON_PATH)  # 3. use this function to add the script to the addon

        # 4. actually, there is no 4.
        # Just continue to use the page as normal,
        # but don't forget to use "mw:" before the main world variables in evaluate
        # (https://camoufox.com/python/main-world-eval)

        await page.goto('https://example.com')


if __name__ == '__main__':
    asyncio.run(main())
```

## How It Works
1. **Script Storage**: JavaScript code is saved to `addon/scripts/` with MD5 hash filenames
2. **Registry Management**: Scripts are tracked in `registry.json` for efficient loading
3. **Extension Injection**: The browser extension reads and executes all registered scripts
4. **Deduplication**: Identical scripts are automatically deduplicated using content hashes

## Project Structure
```
├── addon/                     
│   ├── manifest.json          # Extension manifest
│   ├── inject.js              # Content script for injection
│   └── scripts/               # Generated script files
├── add_init_script.py         # Main API function
├── example.py                 # Usage example
└── requirements.txt           # Dependencies
```
