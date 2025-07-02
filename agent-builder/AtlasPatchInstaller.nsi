OutFile "AtlasPatchInstaller.exe"
InstallDir "$PROGRAMFILES\\AtlasPatch"
RequestExecutionLevel admin
Section "Core"
  SetOutPath $INSTDIR
  File "dist/AtlasPatchAgent/AtlasPatchAgent.exe"
  File "config.json"
  File "ca.crt" "agent1.crt" "agent1.key"
  ExecWait '$INSTDIR/AtlasPatchAgent.exe --startup auto install'
SectionEnd