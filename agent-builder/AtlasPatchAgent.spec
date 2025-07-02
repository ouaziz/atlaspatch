# -*- mode: python -*-
block_cipher = None

hiddenimports = ['wmi', "win32timezone"]

a = Analysis(['agent_service.py'],
             pathex=['.'],
             binaries=[],
             datas=[('config.json', '.'), ('ca.crt', '.'), ('agent1.crt', '.'), ('agent1.key', '.')],
             hiddenimports=hiddenimports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='AtlasPatchAgent',
          debug=False, bootloader_ignore_signals=False, strip=False, upx=True)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas,
               strip=False, upx=True, name='AtlasPatchAgent')