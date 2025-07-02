# pour generer les certificats serveur et agent
./generate_certs.sh 

# builder le .exe
.\build_agent.ps1

# builder le .msi
makensis AtlasPatchInstaller.nsi