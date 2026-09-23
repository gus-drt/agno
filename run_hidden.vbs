Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptDir
WshShell.Run """" & scriptDir & "\venv\Scripts\python.exe"" """ & scriptDir & "\main.py""", 0, False
