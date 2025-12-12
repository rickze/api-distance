<#
Automated deploy script for API_GPS on Windows.

Usage (run as Administrator PowerShell):
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
    .\scripts\deploy_windows.ps1 -InstallPython -TomTomKey "YOUR_KEY_HERE"

Options:
    -InstallPython : try to install Python via winget if not present
    -TomTomKey     : (optional) TomTom API key to set in config.env or as machine env var
    -ServicePort   : port for the service (default 8010)
    -ServiceName   : name of the NSSM service (default API_GPS_Distance)

Notes:
- Script attempts automated steps but may fallback to manual actions if winget/choco not present.
- Run as Administrator.
- Reviewed and safe but use cautiously in production.
#>

param(
    [switch]$InstallPython,
    [string]$TomTomKey,
    [int]$ServicePort = 8010,
    [string]$ServiceName = "API_GPS_Distance"
)

function Test-Admin {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Error "This script must be run as Administrator. Exiting."
        exit 1
    }
}

function Install-PythonIfMissing {
    Write-Host "Checking for python..."
    try {
        $py = & python --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Python found: $py"
            return
        }
    } catch { }

    if ($InstallPython) {
        Write-Host "Attempting to install Python via winget..."
        try {
            winget install --id Python.Python.3 -e --accept-package-agreements --accept-source-agreements
            Write-Host "winget install completed."
            return
        } catch {
            Write-Warning "winget install failed or not available. Will try Chocolatey if present."
        }

        try {
            choco install python -y
            Write-Host "Chocolatey install completed."
            return
        } catch {
            Write-Warning "Chocolatey not available or install failed. Please install Python 3.12+ manually from https://www.python.org/downloads and ensure it's on PATH."
            exit 1
        }
    } else {
        Write-Warning "Python not found. Re-run with -InstallPython or install Python manually."
        exit 1
    }
}

function Ensure-DirectoryAndCopy {
    param(
        [string]$TargetDir
    )
    if (-not (Test-Path -Path $TargetDir)) {
        New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
        Write-Host "Created $TargetDir"
    }

    # Copy all project files from current path to target
    $source = (Get-Location).ProviderPath
    Write-Host "Copying project files from $source to $TargetDir"
    robocopy $source $TargetDir /MIR /XD .git .github .vs  | Out-Null
}

function New-VenvAndInstallDeps {
    param(
        [string]$TargetDir
    )
    $venvPath = Join-Path $TargetDir 'venv'
    if (-not (Test-Path $venvPath)) {
        Write-Host "Creating virtualenv..."
        & python -m venv $venvPath
    } else {
        Write-Host "Virtualenv already exists at $venvPath"
    }

    $activate = Join-Path $venvPath 'Scripts\Activate.ps1'
    Write-Host "Installing runtime dependencies from requirements.txt"
    & $venvPath\Scripts\python.exe -m pip install --upgrade pip
    & $venvPath\Scripts\python.exe -m pip install -r (Join-Path $TargetDir 'requirements.txt')
}

function Set-ConfigEnv {
    param(
        [string]$TargetDir,
        [string]$Key
    )
    $configPath = Join-Path $TargetDir 'config.env'
    if (-not (Test-Path $configPath)) {
        if (Test-Path (Join-Path $TargetDir 'env.sample')) {
            Copy-Item -Path (Join-Path $TargetDir 'env.sample') -Destination $configPath
            Write-Host "Copied env.sample to config.env"
        } else {
            New-Item -Path $configPath -ItemType File | Out-Null
        }
    }
    if ($Key) {
        Write-Host "Setting TOMTOM_API_KEY in config.env"
        $content = Get-Content $configPath -Raw
        if ($content -match 'TOMTOM_API_KEY=') {
            $new = ($content -replace 'TOMTOM_API_KEY=.*', "TOMTOM_API_KEY=$Key")
            Set-Content -Path $configPath -Value $new
        } else {
            Add-Content -Path $configPath -Value "TOMTOM_API_KEY=$Key"
        }
        # Also set machine environment variable
        [Environment]::SetEnvironmentVariable('TOMTOM_API_KEY', $Key, 'Machine')
        Write-Host "TOMTOM_API_KEY set as machine environment variable (requires restart for some services)."
    } else {
        Write-Host "No TOMTOM key provided. Ensure config.env contains TOMTOM_API_KEY or set system env var."
    }
}

function Ensure-NSSM {
    # Try winget, choco, then manual fallback
    Write-Host "Checking for nssm..."
    $nssmPath = (Get-Command nssm -ErrorAction SilentlyContinue)?.Source
    if ($nssmPath) {
        Write-Host "nssm found at $nssmPath"
        return $nssmPath
    }

    Write-Host "nssm not found. Attempting to install via winget..."
    try {
        winget install -e --id nssm.nssm
        $nssmCmd = Get-Command nssm -ErrorAction SilentlyContinue
        if ($nssmCmd) { 
            $nssmPath = $nssmCmd.Source
            Write-Host "nssm installed via winget: $nssmPath"; return $nssmPath 
        }
    } catch { Write-Warning "winget install nssm failed or not available." }

    Write-Host "Attempting Chocolatey install of nssm..."
    try {
        choco install nssm -y
        $nssmCmd = Get-Command nssm -ErrorAction SilentlyContinue
        if ($nssmCmd) { 
            $nssmPath = $nssmCmd.Source
            Write-Host "nssm installed via choco: $nssmPath"; return $nssmPath 
        }
    } catch { Write-Warning "choco install nssm failed or not available." }

    Write-Warning "Automatic nssm install failed. Please download nssm from https://nssm.cc/download and place nssm.exe on PATH (e.g., C:\Windows\System32)."
    return $null
}

function Install-Service-With-NSSM {
    param(
        [string]$TargetDir,
        [string]$ServiceName,
        [int]$Port
    )
    $nssmCmd = Get-Command nssm -ErrorAction SilentlyContinue
    if (-not $nssmCmd) { Write-Error "nssm not found. Cannot create service."; return }
    $nssmExe = $nssmCmd.Source

    $pythonExe = Join-Path $TargetDir '\venv\Scripts\python.exe'
    if (-not (Test-Path $pythonExe)) { $pythonExe = (Get-Command python).Source }

    $arguments = "-m uvicorn main:app --host 0.0.0.0 --port $Port"

    Write-Host "Installing service $ServiceName using nssm"
    & nssm install $ServiceName $pythonExe $arguments

    # Optionally configure working directory
    & nssm set $ServiceName AppDirectory $TargetDir

    # Configure restart on failure
    & nssm set $ServiceName AppRestartDelay 5000

    Write-Host "Service installed. Setting recovery options and starting service."
    Start-Service -Name $ServiceName -ErrorAction SilentlyContinue
}

function Open-FirewallPort {
    param(
        [int]$Port
    )
    Write-Host "Creating firewall rule for port $Port"
    New-NetFirewallRule -DisplayName "API_GPS_Distance_Inbound" -Direction Inbound -Protocol TCP -LocalPort $Port -Action Allow -Profile Any -ErrorAction SilentlyContinue
}

# ----------------- Main -----------------
Test-Admin

$target = "C:\\APIs\\GPS_DISTANCE"
Ensure-DirectoryAndCopy -TargetDir $target

Install-PythonIfMissing
New-VenvAndInstallDeps -TargetDir $target
Set-ConfigEnv -TargetDir $target -Key $TomTomKey

$nssm = Ensure-NSSM
if ($nssm) {
    Install-Service-With-NSSM -TargetDir $target -ServiceName $ServiceName -Port $ServicePort
} else {
    Write-Warning "nssm not available - please install it manually and re-run the script's NSSM step."
}

Open-FirewallPort -Port $ServicePort

Write-Host "Deployment script finished. Check service with Get-Service -Name $ServiceName and logs."