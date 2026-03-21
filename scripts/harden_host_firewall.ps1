# harden_host_firewall.ps1
# Blocks incoming traffic on ports 5433, 8000, 6379 from Public and Private network profiles
Push-Location

Write-Host "Engineering Windows Defender Firewall for CoreGraph Network Isolation..."

# PostgreSQL loopback constraint
New-NetFirewallRule -DisplayName "CoreGraph-Block-Ext-PG" -Direction Inbound -LocalPort 5433 -Protocol TCP -Action Block -Profile Public,Private -ErrorAction SilentlyContinue

# ASGI Gateway local constraint
New-NetFirewallRule -DisplayName "CoreGraph-Block-Ext-ASGI" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Block -Profile Public,Private -ErrorAction SilentlyContinue

# Redis isolation (6379 natively not bound but blocking anyway)
New-NetFirewallRule -DisplayName "CoreGraph-Block-Ext-Redis" -Direction Inbound -LocalPort 6379 -Protocol TCP -Action Block -Profile Public,Private -ErrorAction SilentlyContinue

Write-Host "Zero-Trust boundaries applied to host interfaces."
Pop-Location
