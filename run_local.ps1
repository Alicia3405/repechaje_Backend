# ============================================================
#  Arranque LOCAL del backend (Emergencias Vehiculares API)
#  Enlaza a 0.0.0.0:8000 para que el CELULAR pueda conectarse
#  usando la IP del PC (ver flutter/lib/config/api_config.dart).
# ============================================================
#  Uso:   .\run_local.ps1
#  Requisitos: el celular y este PC en la MISMA red Wi-Fi.
# ============================================================

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

# IP local de la Wi-Fi/Ethernet real (excluye adaptadores virtuales WSL/Hyper-V/Docker)
$ip = (Get-NetIPAddress -AddressFamily IPv4 |
       Where-Object {
         $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' -and
         $_.InterfaceAlias -notlike '*vEthernet*' -and $_.InterfaceAlias -notlike '*WSL*' -and
         $_.InterfaceAlias -notlike '*Loopback*'
       } |
       Sort-Object { if ($_.InterfaceAlias -like '*Wi-Fi*') {0} else {1} } |
       Select-Object -First 1 -ExpandProperty IPAddress)
if (-not $ip) { $ip = '192.168.1.11' }

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Backend LOCAL -> base de datos: bdflas" -ForegroundColor Cyan
Write-Host " PC (esta maquina):  http://$ip:8000" -ForegroundColor Green
Write-Host " Docs (Swagger):     http://$ip:8000/docs" -ForegroundColor Green
Write-Host " El celular debe apuntar a: http://$ip:8000" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

# Arranca uvicorn en TODAS las interfaces (0.0.0.0)
& ".\venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
