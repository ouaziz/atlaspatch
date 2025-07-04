param(
  [string]$CertCN = "agent1",
  [string]$BuildDir = "C:/agent-builder"
)
# creat folder
# New-Item -ItemType Directory -Path $BuildDir -Force

# 1. Copier certificats
# Copy-Item ../certs/$CertCN.* $BuildDir
# Copy-Item ../certs/ca.crt $BuildDir
# Copy-Item config_template.json $BuildDir

# Set-Location $BuildDir

# 2. Créer config.json
(Get-Content config_template.json) -replace 'atlaspatch.example.com', 'atlaspatch.local' | Set-Content config.json

# 3. Build EXE
pip install -r requirements.txt
pyinstaller --clean AtlasPatchAgent.spec

# 4. (optionnel) Signature code
# signtool sign /f mycode.pfx /p $env:PFX_PASS /tr http://timestamp.digicert.com /td sha256 dist/AtlasPatchAgent.exe

# 5. Créer installeur NSIS ou WiX