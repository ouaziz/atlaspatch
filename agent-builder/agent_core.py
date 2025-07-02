import json, time, subprocess, requests, psutil, platform, wmi, hashlib
from pathlib import Path

CONFIG = json.load(open(Path(__file__).with_name('local_config.json')))
SERVER = CONFIG['server_url']

session = requests.Session()
session.cert = (CONFIG['cert'], CONFIG['key'])
session.verify = CONFIG['ca']

def get_hardware_uuid() -> str:
    """
    Returns a 32-char hexadecimal UUID for this machine.

    Order of preference
    -------------------
    1. Win32_ComputerSystemProduct.UUID      ← real firmware UUID
    2. `wmic csproduct get uuid`             ← fallback when WMI fails inside service
    3. MAC-address hash (last-ditch)         ← guarantees global uniqueness
    """
    # --- 1) Regular WMI call --------------------------------------------
    try:
        c = wmi.WMI(namespace="root\\CIMV2")
        uuid = c.Win32_ComputerSystemProduct()[0].UUID
        if uuid and uuid != "FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF":
            # standardise: upper-case, no braces, no dashes
            return uuid.replace("{", "").replace("}", "").replace("-", "").upper()
    except Exception:
        pass

    # --- 2) Fallback: shell out to wmic ----------------------------------
    try:
        output = subprocess.check_output(
            ["wmic", "csproduct", "get", "uuid"], text=True, timeout=5
        )
        uuid = [line.strip() for line in output.splitlines() if line.strip()][1]
        if uuid:
            return uuid.replace("-", "").upper()
    except Exception:
        pass

    # --- 3) Last resort: hash the first NIC MAC --------------------------
    import uuid as py_uuid
    mac = py_uuid.getnode().to_bytes(6, "big")
    return hashlib.sha256(mac).hexdigest()[:32].upper()

def collect_metrics():
    return {
        'hardware_uuid': get_hardware_uuid(),
        'hostname': platform.node(),
        'version': '1.0.0',
        'cpu': psutil.cpu_percent(interval=1),
        'mem': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('C:/').percent,
    }

def send_heartbeat():
    payload = collect_metrics()
    print(payload)
    try:
        r = session.post(SERVER + 'heartbeat/', json=payload, timeout=15)
        r.raise_for_status()
        return r.json().get('commands', [])
    except requests.exceptions.RequestException as e:
        return []

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
            print("Heartbeat...")
            cmds = send_heartbeat()
            for c in cmds:
                cid = c['id']
                typ = c['type']
                status = 'done'
                log = ''
                try:
                    if typ == 'UPGRADE_APPS':
                        print("Upgrade apps...")
                        exec_upgrade_apps()
                    elif typ == 'UPDATE_OS':
                        print("Update OS...")
                        exec_update_os()
                    elif typ == 'STOP_AGENT':
                        status = 'done'
                        report(cid, status, 'stopping')
                        return  # handled by service wrapper
                except Exception as e:
                    status = 'failed'
                    log = str(e)
                report(cid, status, log)
        except Exception as e:
            pass  # réseau KO ⇒ nouvelle tentative
        time.sleep(CONFIG['poll_interval'])

if __name__ == '__main__':
    main_loop()
    