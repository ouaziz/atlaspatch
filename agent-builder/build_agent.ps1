param(
  [string]$CertCN = "atlaspatch-agent-1",
  [string]$BuildDir = "C:/agent-builder"
)
# creat folder
New-Item -ItemType Directory -Path $BuildDir -Force
Set-Location $BuildDir

# 1. Copier certificats
Copy-Item ../certs/$CertCN.* .
Copy-Item ../certs/ca.crt .

# 2. Créer config.json
(Get-Content config_template.json) -replace 'atlaspatch.example.com', 'atlaspatch.local' | Set-Content config.json

# 3. Build EXE
pip install -r requirements.txt
pyinstaller --clean --onefile --noconsole AtlasPatchAgent.spec

# 4. (optionnel) Signature code
# signtool sign /f mycode.pfx /p $env:PFX_PASS /tr http://timestamp.digicert.com /td sha256 dist/AtlasPatchAgent.exe

# 5. Créer installeur NSIS ou WiX