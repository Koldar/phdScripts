param (
    [string]$target = "all"
)

$PLANTUML_JAR = "C:\Program Files\plantuml\plantuml.1.2020.6.jar"

Write-Output $target

if ($target -eq "uml") {
    Get-ChildItem -Path src/plantumls -Filter *.plantuml -Recurse -File -Name | ForEach-Object {
        Write-Output($_)
        & java.exe -jar $PLANTUML_JAR src/plantumls/$_ -output "../images/plantumls/"
    }
} else {
    & lualatex.exe --halt-on-error --file-line-error --shell-escape "main.tex"
    if ($target -eq "all") {
        & bibtex.exe -quiet "main"
        & makeindex.exe -s main.ist -o main.gls main.glo 
        & makeglossaries-lite.exe -q "main"
        & lualatex.exe --halt-on-error --file-line-error --shell-escape "main.tex"
        & lualatex.exe --halt-on-error --file-line-error --shell-escape "main.tex"
    }
}

Write-Output "DONE!"