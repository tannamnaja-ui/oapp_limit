Dim WshShell, strDir, strNode
Set WshShell = CreateObject("WScript.Shell")

strDir = WshShell.ExpandEnvironmentStrings("%ProgramFiles%\oapp_limit")

' Kill any existing node process for this app
On Error Resume Next
WshShell.Run "cmd /c tasklist | findstr node.exe > nul && taskkill /F /IM node.exe /T > nul 2>&1", 0, True
On Error GoTo 0

WScript.Sleep 500

' Start node server in background (hidden)
WshShell.CurrentDirectory = strDir
WshShell.Run "cmd /c node server.js > """ & strDir & "\server.log"" 2>&1", 0, False

' Wait for server to start
WScript.Sleep 2500

' Open browser
WshShell.Run "http://localhost:3300"

Set WshShell = Nothing
