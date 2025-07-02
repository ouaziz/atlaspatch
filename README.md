# pour generer les certificats serveur et agent
./generate_certs.sh 

# builder le .exe
.\build_agent.ps1

# builder le .msi
makensis AtlasPatchInstaller.nsi



#####################################
# configuration
pip install pywin32
python -m pywin32_postinstall -install
pip install win32timezone

# creae exe
pyinstaller --hiddenimport win32timezone --onefile agent.py

# install
python agent.py install

# start
python agent.py start

# stop 
python agent.py stop

# uninstall
python agent.py uninstall

# Add to Windows Startup
## Create a batch file:

@echo off
pythonw C:\path\to\agent.py

## Place it in:
C:\Users\YourUsername\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup

# Security & Considerations
- Ensure compliance with user privacy laws (GDPR, etc.).
- Encrypt or secure the API communication.
- Encryption: Use HTTPS for API requests.
- Authentication: Add API keys or tokens.
- Use an executable (pyinstaller --onefile agent.py) for easier distribution.
