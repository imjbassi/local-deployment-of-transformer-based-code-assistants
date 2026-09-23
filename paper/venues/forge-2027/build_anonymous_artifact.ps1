param([string]$Python = "python")
$ErrorActionPreference = "Stop"
& $Python (Join-Path $PSScriptRoot "build_anonymous_artifact.py")
if ($LASTEXITCODE -ne 0) { throw "Artifact build failed" }
