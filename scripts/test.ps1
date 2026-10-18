param (
    [Parameter(Mandatory=$true, HelpMessage="Path to the folder containing the PDF files")]
    [string]$InputFolder,

    [Parameter(Mandatory=$true, HelpMessage="Path to the folder where the MD files will be saved")]
    [string]$OutputFolder
)

# Verify the input folder exists
if (-not (Test-Path -Path $InputFolder)) {
    Write-Error "The input folder '$InputFolder' does not exist."
    exit
}

# Create the output folder if it does not exist
if (-not (Test-Path -Path $OutputFolder)) {
    Write-Host "Output folder not found. Creating '$OutputFolder'..."
    New-Item -ItemType Directory -Path $OutputFolder | Out-Null
}

# Get all .pdf files in the input directory
$pdfFiles = Get-ChildItem -Path $InputFolder -Filter "*.pdf" -File

if ($pdfFiles.Count -eq 0) {
    Write-Host "No PDF files found in '$InputFolder'."
    exit
}

foreach ($file in $pdfFiles) {
    # 1. Get the name of the file without the .pdf extension
    $baseName = $file.BaseName
    
    # 2. Replace " - " with "_"
    $newName = $baseName.Replace(" - ", "_")
    
    # 3. Replace all remaining spaces with "_"
    $newName = $newName.Replace(" ", "_")
    
    # 4. Construct the new file path with a .md extension
    $newFilePath = Join-Path -Path $OutputFolder -ChildPath "$newName.md"
    
    # 5. Create the new empty .md file
    New-Item -ItemType File -Path $newFilePath -Force | Out-Null
    
    Write-Host "Created: $newName.md"
}

Write-Host "Process completed successfully."