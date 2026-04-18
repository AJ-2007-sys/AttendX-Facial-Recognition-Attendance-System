# Fix Windows Camera Permissions for Desktop Apps (like Python)
# This overrides the "Allow desktop apps to access your camera" setting in Windows Privacy.

$registryPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam"

try {
    # Check if the path exists, if not, it will be handled
    if (!(Test-Path $registryPath)) {
        New-Item -Path $registryPath -Force | Out-Null
    }

    # Set the value to "Allow"
    Set-ItemProperty -Path $registryPath -Name "Value" -Value "Allow" -ErrorAction Stop
    Write-Host "Success: Desktop apps are now allowed to access the camera." -ForegroundColor Green
    Write-Host "Please restart the Python application." -ForegroundColor Yellow
} catch {
    Write-Host "Error: Could not modify registry. Please run this script as Administrator." -ForegroundColor Red
    Write-Host $_.Exception.Message
}

# Keep window open to read
Read-Host -Prompt "Press Enter to exit"
