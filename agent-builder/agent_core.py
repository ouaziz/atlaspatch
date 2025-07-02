import json, time, subprocess, requests, psutil, platform
from pathlib import Path

CONFIG = json.load(open(Path(__file__).with_name('config.json')))
SERVER = CONFIG['server_url']

session = requests.Session()
session.cert = (CONFIG['cert'], CONFIG['key'])
session.verify = CONFIG['ca']

def collect_metrics():
    return {
        'hostname': platform.node(),
        'version': '1.0.0',
        'cpu': psutil.cpu_percent(interval=1),
        'mem': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('C:/').percent,
    }

def send_heartbeat():
    payload = collect_metrics()
    r = session.post(SERVER + 'heartbeat/', json=payload, timeout=15)
    r.raise_for_status()
    return r.json().get('commands', [])

def exec_upgrade_apps():
    subprocess.run(['winget', 'upgrade', '--all', '--silent', '--accept-source-agreements', '--accept-package-agreements'],
                   capture_output=True, text=True, timeout=3600)

def exec_update_os():
    ps = ['powershell', '-Command', 'Import-Module PSWindowsUpdate; Install-WindowsUpdate -AcceptAll -AutoReboot -IgnoreReboot']
    subprocess.run(ps, capture_output=True, text=True)

def report(cid, status, log):
    session.post(f"{SERVER}commands/{cid}/result/", json={'status': status, 'log': log[:4000]})

def main_loop():
    while True:
        try:
            cmds = send_heartbeat()
            for c in cmds:
                cid = c['id']
                typ = c['type']
                status = 'done'
                log = ''
                try:
                    if typ == 'UPGRADE_APPS':
                        exec_upgrade_apps()
                    elif typ == 'UPDATE_OS':
                        exec_update_os()
                    elif typ == 'STOP_AGENT':
                        status = 'done'
                        report(cid, status, 'stopping')
                        return  # handled by service wrapper
                except Exception as e:
                    status = 'failed'
                    log = str(e)
                report(cid, status, log)
        except Exception:
            pass  # réseau KO ⇒ nouvelle tentative
        time.sleep(CONFIG['poll_interval'])