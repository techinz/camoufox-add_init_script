import asyncio
import os

from camoufox import AsyncCamoufox

from add_init_script import add_init_script, clean_scripts

# path to the addon directory, relative to the script location (default 'addon')
ADDON_PATH = 'addon'


async def main():
    # script that has to load before page does
    # (exactly this script is not mine and doesn't always work on the first try, but the main thing is that it does work at all thanks to this temporary solution)
    script = '''
    console.clear = () => console.log('Console was cleared');

    function setupIntercept() {
      if (window.turnstile) {
        window.turnstile.render = (a, b) => {
          let params = {
            sitekey: b.sitekey,
            pageurl: window.location.href,
            data: b.cData,
            pagedata: b.chlPageData,
            action: b.action,
            userAgent: navigator.userAgent,
            json: 1,
          };
    
          console.log('intercepted-params:' + JSON.stringify(params));
          window.cfCallback = b.callback;
          window.cfParams = params;
    
          if (interval) {
            clearInterval(interval);
          }
    
          return;
        };
      }
    }
    
    const interval = setInterval(() => {
      setupIntercept()
    }, 50);
    
    setupIntercept();
    
    console.log('Script 1 initialized');
    '''

    async with AsyncCamoufox(
            headless=True,
            main_world_eval=True,  # 1. add this to enable main world evaluation
            addons=[os.path.abspath(ADDON_PATH)]  # 2. add this to load the addon that will inject the scripts on init
    ) as browser:
        page = await browser.new_page()

        clean_scripts(ADDON_PATH)  # 3. clean the old scripts before use

        # use add_init_script() instead of page.add_init_script()
        await add_init_script(script, ADDON_PATH)  # 4. use this function to add the script to the addon

        # 4. actually, there is no 4.
        # Just continue to use the page as normal,
        # but don't forget to use "mw:" before the main world variables in evaluate
        # (https://camoufox.com/python/main-world-eval)

        await page.goto('https://nopecha.com/demo/cloudflare', wait_until='networkidle')

        await page.wait_for_timeout(5000)  # wait for page to load (just in case)

        params = await page.evaluate('mw:window.cfParams')  # use "mw:" to access main world variables

        print(f'Intercepted Cloudflare parameters: {params}')

        assert params is not None, "Cloudflare parameters should not be None"


if __name__ == '__main__':
    asyncio.run(main())
