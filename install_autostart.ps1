$WshShell = New-Object -comObject WScript.Shell
$StartupFolder = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$ShortcutPath = "$StartupFolder\AgnoBot.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = """c:\Users\duart\Downloads\Projetos\Agno\run_hidden.vbs"""
$Shortcut.WorkingDirectory = "c:\Users\duart\Downloads\Projetos\Agno"
$Shortcut.Save()

Write-Host "Atalho criado com sucesso na pasta Inicializar do Windows!"
Write-Host "O bot iniciar automticamente sempre que o PC for ligado."
