import json, time, subprocess, requests, psutil, platform, wmi, hashlib
import datetime as dt
import tempfile, uuid, pathlib
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler


CONFIG = json.load(open(Path(__file__).with_name('local_config.json')))
SERVER = CONFIG['server_url']

session = requests.Session()
session.cert = (CONFIG['cert'], CONFIG['key'])
session.verify = CONFIG['ca']

# Set up logging
log_file = 'C:/Program Files (x86)/AtlasPatch/agent_atlaspatch.log'
logging.basicConfig(
    handlers=[RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)],
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AtlasPatchAgent')


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

def collect_inventory_winget():
    """
    Retourne [{name, version, captured_at}, …] pour tous les logiciels installés.
    Utilise d'abord `winget list --output json`, puis retombe sur `winget export`
    si l'option JSON n'est pas prise en charge.
    """
    def _now():
        return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

    try:
        output = subprocess.check_output(
            ["winget", "list", "--output", "json"],
            text=True, encoding="utf-8", errors="ignore"
        )
        pkgs = json.loads(output)          # liste de dicts
    except subprocess.CalledProcessError:
        # Fallback : export → on lit le fichier généré
        temp = pathlib.Path(tempfile.gettempdir()) / f"winget_{uuid.uuid4().hex}.json"
        subprocess.check_call([
            "winget", "export",
            "--include-versions",
            "--accept-source-agreements",
            "-o", str(temp)
        ])
        export = json.load(temp.open())
        pkgs = export["Sources"][0]["Packages"]   # structure différente

    inventory = []
    for pkg in pkgs:
        inventory.append({
            "name":     pkg.get("Name") or pkg.get("PackageIdentifier"),
            "version":  pkg.get("Version", "").strip() or           # sortie `list`
                        pkg.get("InstalledVersion", "").strip() or  # sortie `list` (vieux)
                        pkg.get("PackageVersion", "").strip() or    # sortie `show` éventuelle
                        "",                             # rien dans l’export
            "captured_at": _now(),
        })
    return inventory


def collect_metrics():
    return {
        'hardware_uuid': get_hardware_uuid(),
        'hostname': platform.node(),
        'version': '1.0.0',
        'cpu': psutil.cpu_percent(interval=1),
        'mem': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('C:/').percent,
        'inventory': collect_inventory_winget(),
    }

def send_heartbeat():
    payload = collect_metrics()
    try:
        r = session.post(SERVER + 'heartbeat/', json=payload, timeout=15)
        r.raise_for_status()
        return r.json().get('commands', [])
    except requests.exceptions.RequestException as e:
        print(f"Heartbeat failed: {e}")
        logger.error(f"Heartbeat failed: {e}")
        return []

def exec_upgrade_all_apps():
    subprocess.run(['winget', 'upgrade', '--all', '--silent', '--accept-source-agreements', '--accept-package-agreements'],
                   capture_output=True, text=True, timeout=3600)

def exec_update_os():
    ps = ['powershell', '-Command', 'Import-Module PSWindowsUpdate; Install-WindowsUpdate -AcceptAll -AutoReboot -IgnoreReboot']
    subprocess.run(ps, capture_output=True, text=True)

def report(cid, status, log):
    session.post(f"{SERVER}commands/{cid}/result/", json={'status': status, 'log': log[:4000]})

def main_loop():
    logger.info("Starting main loop...")
    print("Starting main loop...")
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
                    if typ == 'UPGRADE_ALL_APPS':
                        print("Upgrade all apps...")
                        exec_upgrade_all_apps()
                    elif typ == 'UPGRADE_APP':
                        print("Upgrade app...")
                        exec_upgrade_app()
                    elif typ == 'UPDATE_OS':
                        print("Update OS...")
                        exec_update_os()
                    elif typ == 'STOP_AGENT':
                        print("Stopping agent...")
                        status = 'done'
                        report(cid, status, 'stopping')
                        return  # handled by service wrapper
                except Exception as e:
                    print(f"Command failed: {e}")
                    logger.error(f"Command failed: {e}")
                    status = 'failed'
                    log = str(e)
                report(cid, status, log)
        except Exception as e:
            logger.error(f"Heartbeat failed: {e}")
            print(f"Heartbeat failed-: {e}")
            pass  # réseau KO ⇒ nouvelle tentative
        time.sleep(CONFIG['poll_interval'])

if __name__ == '__main__':
    main_loop()
    