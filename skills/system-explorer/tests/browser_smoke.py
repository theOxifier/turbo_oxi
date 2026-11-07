"""Optional integration checks: Python Playwright + an installed Chromium."""
import asyncio
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import sys
import tempfile
from threading import Thread

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from render import render
from validate_model import load_model
from playwright.async_api import async_playwright


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        dest=Path(tmp)
        class QuietHandler(SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=tmp))
        Thread(target=server.serve_forever,daemon=True).start()
        base=f'http://127.0.0.1:{server.server_port}/'
        async with async_playwright() as p:
            executable=shutil.which('chromium') or shutil.which('chromium-browser')
            browser=await p.chromium.launch(**({'executable_path':executable} if executable else {}),headless=True,args=['--no-sandbox'])
            page=await browser.new_page(viewport={'width':1500,'height':1000},reduced_motion='reduce')
            errors=[]
            requests=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('request',lambda req:requests.append(req.url))
            for name in ['software-system','approval-process']:
                model=load_model(ROOT/'examples'/f'{name}.json')
                path=dest/f'{name}.html';path.write_text(render(model))
                await page.goto(base+path.name)
                assert await page.title()==model['title']+' · System Explorer'
                assert await page.locator('.entity').count()==len([e for e in model['entities'] if 'parent_id' not in e])
                entity=model['entities'][0]
                edge=model['relationships'][0]
                await page.get_by_role('button',name='Inspect relationship: '+edge['label'],exact=True).click()
                assert edge['description'] in await page.locator('#inspector').inner_text()
                await page.get_by_role('button',name='Inspect entity: '+entity['label'],exact=True).click()
                assert entity['description'] in await page.locator('#inspector').inner_text()
                await page.locator('#scenarios button').first.click()
                await page.locator('#next').click()
                assert await page.locator('#progress').inner_text()==f"1 / {len(model['scenarios'][0]['events'])}"
                assert await page.locator('.edge.current').count()==1
                first_state=list(model['scenarios'][0]['events'][0]['state_changes'].values())[0]
                assert first_state in await page.locator('#canvas').inner_text()
                await page.locator('#next').click()
                await page.locator('#prev').click()
                assert await page.locator('#progress').inner_text()==f"1 / {len(model['scenarios'][0]['events'])}"
                await page.locator('#reset').click()
                assert await page.locator('.edge.current').count()==0
                await page.get_by_role('button',name='Inspect entity: '+entity['label'],exact=True).click()
                assert entity['initial_state'] in await page.locator('#inspector').inner_text()
                await page.locator('#sequence-tab').click()
                assert await page.locator('.sequence-event').count()==len(model['scenarios'][0]['events'])
                await page.get_by_role('button',name='Event 2: '+model['scenarios'][0]['events'][1]['label'],exact=True).click()
                assert await page.locator('#progress').inner_text()==f"2 / {len(model['scenarios'][0]['events'])}"
                # Switching to failure/revision must clear all prior scenario state.
                await page.locator('#scenarios button').nth(1).click()
                assert (await page.locator('#progress').inner_text()).startswith('0 /')
                await page.locator('#map-tab').click()
                for _ in model['scenarios'][1]['events']:
                    await page.locator('#next').click()
                assert await page.locator('#next').is_disabled()
                await page.locator('#reset').click()
                await page.locator('#speed').select_option('2')
                await page.locator('#play').click()
                await page.wait_for_function("() => document.getElementById('next').disabled",timeout=10000)
                assert await page.locator('#play').inner_text()=='Play'
                await page.locator('#overview').click()
                await page.locator('#search').fill(entity['label'])
                assert await page.locator('.entity').count()==1
                await page.locator('#search').fill('missing-no-entity')
                assert await page.locator('.entity').count()==0
                await page.locator('#search').fill('')
                await page.locator('#group').select_option(entity['group'])
                expected=len([e for e in model['entities'] if e.get('group')==entity['group']])
                assert await page.locator('.entity').count()==expected
                await page.locator('#overview').click()
                assert await page.locator('#group').input_value()==''
                if name=='software-system':
                    await page.get_by_role('button',name='Inspect entity: API service',exact=True).click()
                    await page.get_by_role('button',name='Explore inside →',exact=True).click()
                    assert await page.locator('.entity').count()==2
                    assert 'Request validator' in await page.locator('#canvas').inner_text()
                await page.locator('#overview').click()
                async with page.expect_download() as dl:
                    await page.locator('#download').click()
                downloaded=await dl.value
                assert json.loads(Path(await downloaded.path()).read_text())==model
                await page.set_viewport_size({'width':390,'height':844})
                assert await page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
                await page.locator('#scenarios button').first.click()
                await page.locator('#next').click()
                assert (await page.locator('#progress').inner_text()).startswith('1 /')
                await page.set_viewport_size({'width':1500,'height':1000})
                print(f'PASS {name}: inspect, step, reset, sequence, alternate, playback, search, drill-down, export, mobile')
            # Static models with no edges or scenarios must remain usable.
            model['scenarios']=[];model['relationships']=[]
            path=dest/'static.html';path.write_text(render(model));await page.goto(base+path.name)
            assert await page.locator('#play').is_disabled()
            await page.locator('#sequence-tab').click()
            assert 'Choose a scenario' in await page.locator('#canvas').inner_text()
            # Zero coordinates and a self-edge remain inspectable.
            self_model=load_model(ROOT/'examples/approval-process.json')
            self_model['entities'][0]['x']=0
            self_model['entities'][0]['y']=0
            loop=dict(self_model['relationships'][0],id='self',to='requester',label='Local feedback')
            self_model['relationships'].append(loop)
            self_model['scenarios']=[]
            path=dest/'self.html';path.write_text(render(self_model));await page.goto(base+path.name)
            await page.get_by_role('button',name='Inspect relationship: Local feedback',exact=True).focus()
            await page.keyboard.press('Enter')
            assert 'Local feedback' in await page.locator('#inspector').inner_text()
            # Untrusted labels, payloads and source schemes stay inert.
            model['scenarios']=load_model(ROOT/'examples/approval-process.json')['scenarios']
            model['relationships']=load_model(ROOT/'examples/approval-process.json')['relationships']
            attack='</script><script>window.injected=true</script><img src=x onerror="window.injected=true">'
            model['title']=attack;model['entities'][0]['label']=attack
            model['scenarios'][0]['events'][0]['payload']={'example':attack}
            model['sources']=[{'id':'hostile','label':'Untrusted source','uri':'javascript:window.injected=true'}]
            model['entities'][0]['evidence']['sources']=['hostile']
            path=dest/'hostile.html';path.write_text(render(model));await page.goto(base+path.name)
            await page.locator('.entity').first.click()
            assert await page.locator('#inspector a').count()==0
            await page.locator('#scenarios button').first.click()
            await page.locator('#next').click()
            assert json.loads(await page.locator('#inspector pre').inner_text())['example']==attack
            assert not await page.evaluate('Boolean(window.injected)')
            assert not errors,errors
            assert all(url.startswith(base) for url in requests),requests
            print('PASS static model, inert model text/payload/source links, no external requests, no browser errors')
            await browser.close()
        server.shutdown()
        server.server_close()

if __name__=='__main__':
    asyncio.run(main())
