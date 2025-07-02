OutFile "AtlasPatchInstaller.exe"
InstallDir "$PROGRAMFILES/AtlasPatch"
RequestExecutionLevel admin
Section "Core"
  SetOutPath $INSTDIR
  File "dist/AtlasPatchAgent.exe"
  File "config.json"
  File "ca.crt" "client.crt" "client.key"
  ExecWait '$INSTDIR/AtlasPatchAgent.exe --startup auto install'
SectionEnd