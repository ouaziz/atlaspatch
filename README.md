# pour generer les certificats serveur et agent
./generate_certs.sh 

# builder le .exe
.\build_agent.ps1

# builder le .msi
makensis AtlasPatchInstaller.nsi



#####################################

# install
AtlasPatchAgent.exe install

# start
AtlasPatchAgent.exe start

# stop 
AtlasPatchAgent.exe stop

# uninstall
AtlasPatchAgent.exe remove

# Add to Windows Startup
## Create a batch file:

@echo off
pythonw C:\path\to\agent.py

## Place it in:
C:\Users\YourUsername\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup

