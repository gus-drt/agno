$ScriptDir = $PSScriptRoot
$WshShell = New-Object -comObject WScript.Shell
$StartupFolder = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$ShortcutPath = "$StartupFolder\AgnoBot.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = """$ScriptDir\run_hidden.vbs"""
$Shortcut.WorkingDirectory = "$ScriptDir"
$Shortcut.Save()

Write-Host "Atalho criado com sucesso na pasta Inicializar do Windows!"
Write-Host "O bot iniciara automaticamente sempre que o PC for ligado."
