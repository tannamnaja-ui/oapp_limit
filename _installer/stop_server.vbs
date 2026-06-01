Dim WshShell
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c taskkill /F /IM node.exe /T > nul 2>&1", 0, True
Set WshShell = Nothing
