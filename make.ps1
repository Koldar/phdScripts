param (
    [string]$target = "all",
    [string]$config = "config.ini"
)

# Update this version anytime you update this makefile
$MAKE_VERSION = 1.0.0


function Get-IniContent ($filePath)
{
    $ini = @{};
    switch -regex -file ($FilePath)
    {
        "^\s*$" #empty lines
        {
            continue;
        }
        "^\s*\[\s*(.+)\s*\]\s*$" # Section
        {
            $section = $matches[1];
            #Write-Host "Detected section $section";
            $ini[$section] = @{};
            $CommentCount = 0;
            continue;
        }
        "^;(.*)$" # Comment
        {
            # ignore the comments
            continue;
        }
        "^\s*([a-zA-Z][a-zA-Z0-9_]*?)\s*=\s*(.*)\s*$" # Key
        {
            $key = $matches[1];
            $value = $matches[2];
            #$keys = $ini[$section].Keys;
            #Write-Host "Detected key='$key' value='$value' for section='$section'";
            $ini[$section][$key] = $value;
            continue;
        }
        default {
            throw "Unreadable line '$_'";
        }
    }
    return $ini;
}

function ShowInfo($templateVersion, $notes) {
    Write-Output -ForegroundColor Green "Latex Template version is $templateversion"
	Write-Output "Notes from the developer regarding some notoriuos change in this file: "
	Write-Output -ForegroundColor Yellow "$notes"
}

function Help () {
    Write-Output "Targets are"
    Write-Output " - show-info: allows you to determine the version of this build process plus some information the original developer has left you: such notes refer to changes the original developer has made to this build process"
	Write-Output " - show-variables: print a list of variables (and their default values) you can tweak from the command line"
	Write-Output " - all [DEFAULT]: build the pdf file using the 2 full compilations, one bibtex call and another latex compile run. Slow but generates the correct pdf"
	Write-Output " - fast: build the pdf only by calling latex once. Fast but if new references have been added, this command may leave some references undefined."
	Write-Output " - release: like 'all' but we will create a pdf in the release directory with a semantic versioning. Useful to keep track a versioning without git."
	Write-Output " - clean: claer all the contents of build directory"
	Write-Output " - help: shows this message"
}

function MakeFast ($latexCC, $mainSrc, $latexAdditionalFlags, $latexStandardFlags) {
    $latexAdditionalFlagsArray = $latexAdditionalFlags.Split(" ");
    $latexStandardFlagsArray = $latexStandardFlags.Split(" ");
    $completeLatex = $latexAdditionalFlagsArray + $latexStandardFlagsArray + "$mainSrc.tex";
    & $latexCC $completeLatex;
}

function MakeAll ($latexCC, $bibtexCC, $mainSrc, $bibtexFlags, $latexStandardFlags, $latexAdditionalFlags, $buildFolder) {
    $latexAdditionalFlagsArray = $latexAdditionalFlags.Split(" ");
    $latexStandardFlagsArray = $latexStandardFlags.Split(" ");
    $completeLatex = $latexAdditionalFlagsArray + $latexStandardFlagsArray + "$mainSrc.tex";
    Write-Host -ForegroundColor Green "compiling first time...";
    & $latexCC $completeLatex;

    $bibtexFlagsArray = $bibtexFlags.Split(" ");
    $completeBibtex = $bibtexFlagsArray + "$mainSrc";
    Write-Host -ForegroundColor Green "compiling bibliography...";
    cd $buildFolder
    & $bibtexCC $completeBibtex;
    cd ..

    Write-Host -ForegroundColor Green "compiling second time...";
    & $latexCC $completeLatex;
    Write-Host -ForegroundColor Green "compiling third time...";
    & $latexCC $completeLatex;
}

function MakeClean($buildFolder) {
    Remove-Item -Path $buildFolder -Recurse   
}

function MakeUml ($plantumlJar, $javaExe) {
    Get-ChildItem -Path src/plantumls -Filter *.plantuml -Recurse -File -Name | ForEach-Object {
        Write-Output($_);
        $javaArgs = "-jar", "$plantumlJar", "src/plantumls/$_", "-output", "../images/plantumls/";
        & $javaExe $javaArgs;
    }
}

function MakeRelease($latexCC, $bibtexCC, $mainSrc, $bibtexFlags, $latexStandardFlags, $latexAdditionalFlags, $releaseFolder, $versionFile, $buildFolder, $outputName) {
    MakeAll -latexCC $latexCC -bibtexCC $bibtexCC -mainSrc $mainSrc -bibtexFlags $bibtexFlags -latexStandardFlags $latexStandardFlags -latexAdditionalFlags $latexAdditionalFlags -buildFolder $buildFolder;

    if (Test-Path $versionFile -PathType Leaf) {
    } else {
        "0" | Out-File $versionFile;
    }

    $oldVersion = Get-Content -Path $versionFile;
    $version = $oldVersion -as [int];
    Write-Host -ForegroundColor Blue "Old version to replace is $oldVersion";
    $version = $version + 1;
    $version | Out-File $versionFile;
    $buildPdf = Join-Path -Path $buildFolder -ChildPath "$outputName.pdf";
    $releasePdf = Join-Path -Path $releaseFolder -ChildPath "${releaseName}_$version.0.0.pdf";
    Copy-Item -Path $buildFolder -Destination $releasePdf;
	
	Write-Host -ForegroundColor Green "DONE RELEASING VERSION $version.0.0. It's available in $releaseFolder folder.";
}

function ShowVariables ([String] $buildFolder, [String]$releaseFolder, [String]$latexCC, [String] $bibtexCC, [String] $mainSrc, [String] $outputName, [String] $releaseName,  [String] $latexFlags, [String] $bibtexFlags) {
    Write-Host "You can set these variables from the ini file."
	Write-Host ""
	Write-Host -ForegroundColor Green " - BUILD_FOLDER[defaults to $buildFolder]:"
    Write-Host "represents the folder, relative to the project root directory, where to put the pdf and all the metadata generated by latex. Cleaned with 'make clean' "
	Write-Host -ForegroundColor Green  " - RELEASE_FOLDER[defaults to $releaseFolder]:"
    Write-Host "Folder containing all the releases generated by 'make release'"
	Write-Host -ForegroundColor Green  " - LATEX_CC[defaults to $latexCC]:"
    Write-Host "represents the software represenitng the latex compiler to use"
	Write-Host -ForegroundColor Green  " - BIBTEX_CC[defaults to $bibtexCC]:" 
    Write-Host "represents the software that we will call to build the bibliography"
	Write-Host -ForegroundColor Green  " - MAIN_SRC[defaults to $mainSrc]:" 
    Write-Host "the Latex root source code document that will be use as starting point of the latex build process. The filename is relative to the project root directory. No '.tex' extension is needed since it will be automatically appended (e.g., 'main.tex' should be written as 'main')"
	Write-Host -ForegroundColor Green  " - OUTPUT_NAME[defaults to $outputName]:" 
    Write-Host "name of the output that will be generated inside BUILD_FOLDER. No extension is needed (e.g., 'main.pdf' should be written as 'main')"
	Write-Host -ForegroundColor Green  " - RELEASE_NAME[defaults to $releaseName]:" 
    Write-host "name of the file that will be generated inside RELEASE_FOLDER when a release document is added. Note that we will append to such name the version automatically"
	Write-Host -ForegroundColor Green  " - LATEX_FLAGS[defaults to $latexFlags]:" 
    Write-Host "Additional latex flags that will be used in the build process. Note that LATEXT_STANDARD_FLAGS are automatically added to the build process"
	Write-Host -ForegroundColor Green  " - BIBTEX_FLAGS[defaults to $bibtexFlags]:" 
    Write-Host "Additional latex flags that will be used in the build process when building the bibliography"
}

# Load config
Write-Host -ForegroundColor Green "Reading file '$config'...";
$ini = Get-IniContent($config);
Write-Host -ForegroundColor Green "Read file '$config'";

# PUBLIC PROPERTIES

$buildFolder = $ini["General"]["BUILD_FOLDER"];
$releaseFolder = $ini["General"]["RELEASE_FOLDER"];
$latexCC = $ini["General"]["LATEX_CC"];
$bibtexCC = $ini["General"]["BIBTEX_CC"];
$mainSrc = $ini["General"]["MAIN_SRC"];
$outputName = $ini["General"]["OUTPUT_NAME"];
$releaseName = $ini["General"]["RELEASE_NAME"];
$latexFlags = $ini["General"]["LATEX_FLAGS"];
$bibtexFlags = $ini["General"]["BIBTEX_FLAGS"];
$plantumlJar = $ini["General"]["PLANTUML_JAR"];
$javaExe = $ini["General"]["JAVA_EXE"];

# PROTECTED PROPERTIES

$templateVersion = $ini["General"]["TEMPLATE_VERSION"];
$notes = $ini["General"]["NOTES"];
$latexStandardFlags = "--output-directory=$buildFolder";
$versionFile=$ini["General"]["VERSION_FILE"] = ".version";

###########################
# SCRIPT
###########################

Write-Host -ForegroundColor Green "Windows Makefile version is ${MAKE_VERSION}";
Write-Host -ForegroundColor Green "Making $target...";

if ($target -eq "uml") {
    MakeUml -plantumlJar $plantumlJar -javaExe $javaExe;
    Write-Host -ForegroundColor Green "DONE!"
} elseif ($target -eq "help") {
    Help
} elseif ($target -eq "show-info") {
    ShowInfo -templateVersion $templateVersion -notes $notes;
} elseif ($target -eq "show-variables") {
    ShowVariables -buildFolder $buildFolder -releaseFolder $releaseFolder -latexCC $latexCC -bibtexCC $bibtexCC -mainSrc $mainSrc -outputName $outputName -releaseName $releaseName -latexFlags $latexFlags -bibtexFlags $bibtexFlags;
    Write-Host -ForegroundColor Green "DONE!"
} elseif ($target -eq "fast") {
    MakeFast -latexCC $latexCC -mainSrc $mainSrc -latexStandardFlags $latexStandardFlags -latexAdditionalFlags $latexFlags;
    Write-Host -ForegroundColor Green "DONE!"
} elseif ($target -eq "all") {
    MakeAll -latexCC $latexCC -latexStandardFlags $latexStandardFlags -latexAdditionalFlags $latexFlags -bibtexFlags $bibtexFlags -bibtexCC $bibtexCC -mainSrc $mainSrc -buildFolder $buildFolder;
    Write-Host -ForegroundColor Green "DONE!"
} elseif ($target -eq "release") {
    MakeRelease -latexCC $latexCC -latexStandardFlags $latexStandardFlags -latexAdditionalFlags $latexFlags -bibtexFlags $bibtexFlags -bibtexCC $bibtexCC -mainSrc $mainSrc -releaseFolder $releaseFolder -versionFile $versionFile -buildFolder $buildFolder-outputName $outputName;
    Write-Host -ForegroundColor Green "DONE!"
} elseif ($target -eq "clean") {
    MakeClean -buildFolder $buildFolder;
    Write-Host -ForegroundColor Green "DONE!"
} else {
    throw "target $target not found!"
}