# Launch Hospital Emergency Management System
Write-Host "Launching Hospital Emergency Management System..." -ForegroundColor Cyan
if (Get-Command py -ErrorAction SilentlyContinue) {
    py main.py
} else {
    & "C:\Users\pawar\AppData\Local\Python\bin\python.exe" main.py
}
