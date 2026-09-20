param(
    [string]$Output = "output/forge-2027-anonymous-artifact.zip"
)

$ErrorActionPreference = "Stop"
$venueDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $venueDir "../../..")).Path
$stage = Join-Path $venueDir "build/anonymous-artifact"
$resolvedBuild = (Resolve-Path (Join-Path $venueDir "build")).Path

if (-not $stage.StartsWith($resolvedBuild, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to stage outside the venue build directory: $stage"
}
if (Test-Path -LiteralPath $stage) {
    Remove-Item -LiteralPath $stage -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $stage | Out-Null

$files = @(
    "paper/venues/forge-2027/ARTIFACT_README.md",
    "protocol/published_targets.json",
    "containers/evalplus/Dockerfile",
    "pyproject.toml",
    "scripts/analyze_starcoder2_factorial.py"
)
$files += Get-ChildItem (Join-Path $repoRoot "src") -File -Recurse |
    ForEach-Object { [IO.Path]::GetRelativePath($repoRoot, $_.FullName) }
$files += Get-ChildItem (Join-Path $repoRoot "tests") -File -Recurse -Filter "*.py" |
    Where-Object { $_.Name -ne "test_paper.py" } |
    ForEach-Object { [IO.Path]::GetRelativePath($repoRoot, $_.FullName) }
$files += Get-ChildItem (Join-Path $repoRoot "artifacts/primary") -File -Recurse |
    Where-Object { $_.Name -notlike "*.metadata.json" } |
    ForEach-Object { [IO.Path]::GetRelativePath($repoRoot, $_.FullName) }
$files += Get-ChildItem (Join-Path $repoRoot "artifacts/controls/prompt-newline-ablation") -File |
    Where-Object { $_.Name -notlike "*.metadata.json" -and $_.Name -ne "SHA256SUMS" } |
    ForEach-Object { [IO.Path]::GetRelativePath($repoRoot, $_.FullName) }

foreach ($relative in $files | Sort-Object -Unique) {
    $source = Join-Path $repoRoot $relative
    $targetRelative = if ($relative -eq "paper/venues/forge-2027/ARTIFACT_README.md") {
        "README.md"
    } else {
        $relative
    }
    $target = Join-Path $stage $targetRelative
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
    Copy-Item -LiteralPath $source -Destination $target
}

# Scrub machine-specific absolute paths from textual analysis outputs.
Get-ChildItem $stage -File -Recurse | Where-Object {
    $_.Extension -in ".json", ".jsonl", ".md", ".py", ".toml", ".txt"
} | ForEach-Object {
    [string]$text = Get-Content -Raw -LiteralPath $_.FullName
    $text = $text.Replace($repoRoot, "<REPOSITORY_ROOT>")
    $text = $text -replace '/mnt/c/Users/[^/]+/Desktop/Local-Deployment-of-Transformer-based-Code-Assistants-main', '<REPOSITORY_ROOT>'
    $text = $text -replace 'Jaiveer Bassi', 'Anonymous Author'
    $text = $text -replace 'imjbassi', 'anonymous'
    $text = $text -replace '10\.5281/zenodo\.22848609', '<ANONYMIZED_DOI>'
    $text = $text -replace '10\.5281/zenodo\.22800650', '<ANONYMIZED_DOI>'
    [IO.File]::WriteAllText($_.FullName, $text, [Text.UTF8Encoding]::new($false))
}

$checksums = Get-ChildItem $stage -File -Recurse | Sort-Object FullName | ForEach-Object {
    $relative = [IO.Path]::GetRelativePath($stage, $_.FullName).Replace("\", "/")
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash.ToLowerInvariant()
    "$hash  $relative"
}
[IO.File]::WriteAllLines((Join-Path $stage "SHA256SUMS"), $checksums, [Text.UTF8Encoding]::new($false))

$destination = Join-Path $venueDir $Output
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destination) | Out-Null
if (Test-Path -LiteralPath $destination) {
    Remove-Item -LiteralPath $destination -Force
}
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $destination -CompressionLevel Optimal
Write-Output $destination
