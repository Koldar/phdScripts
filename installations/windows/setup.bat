rem install choco
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

rem software used to build other softwares
choco install --yes openjdk python
rem tools 
choco install --yes plantuml graphviz git git-cola vscode 7zip ccleaner notepadplusplus meld vlc miktex irfanview irfanviewplugins
rem front end
choco install --yes  firefox  thunderbird  foxitreader
rem windows software development
choco install --yes dbeaver mobaxterm
