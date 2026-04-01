# SadTalker Setup
# Run this in PowerShell to download all checkpoints

$dir = "$PSScriptRoot\checkpoints"
New-Item -ItemType Directory -Force -Path $dir | Out-Null

$files = @{
    'SadTalker_V0.0.2_256.safetensors' = 'https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_256.safetensors'
    'SadTalker_V0.0.2_512.safetensors' = 'https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_512.safetensors'
    'mapping_00109-model.pth.tar'      = 'https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar'
    'mapping_00229-model.pth.tar'      = 'https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00229-model.pth.tar'
    'facevid2vid_00189-model.pth.tar'  = 'https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/facevid2vid_00189-model.pth.tar'
    'epoch_20.pth'                     = 'https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/epoch_20.pth'
    'shape_predictor_68_face_landmarks.dat' = 'https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/shape_predictor_68_face_landmarks.dat'
    'hub.zip'                          = 'https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/hub.zip'
}

foreach ($name in $files.Keys) {
    $url = $files[$name]
    $path = Join-Path $dir $name
    if (Test-Path $path) {
        Write-Host "OK   $name (already exists)" -ForegroundColor Green
        continue
    }
    Write-Host "DL   $name ..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $url -OutFile $path -UseBasicParsing
        Write-Host "DONE $name" -ForegroundColor Green
    } catch {
        Write-Host "FAIL $name - $_" -ForegroundColor Red
    }
}

# Extract hub.zip
$hubZip = Join-Path $dir 'hub.zip'
if (Test-Path $hubZip) {
    $hubDir = Join-Path $dir 'hub'
    New-Item -ItemType Directory -Force -Path $hubDir | Out-Null
    Expand-Archive -Path $hubZip -DestinationPath $hubDir -Force
    Write-Host "Extracted hub.zip" -ForegroundColor Green
}

Write-Host "`nSetup complete!" -ForegroundColor Cyan
Write-Host "Required files:" -ForegroundColor Cyan
Get-ChildItem $dir | ForEach-Object { Write-Host "  $($_.Name) ($([math]::Round($_.Length/1MB, 1)) MB)" }
