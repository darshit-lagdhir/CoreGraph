param (
    [switch]$Unlock
)

$RootPath = (Get-Item -Path ".\").FullName
$WorkspacePath = "$RootPath\.workspace"

$Items = @(
    "$WorkspacePath\task-matrix.json",
    "$WorkspacePath\project-context.md",
    "$WorkspacePath\manifest.json",
    "$WorkspacePath\manifest.json.sig",
    "$RootPath\Makefile",
    "$RootPath\docker-compose.yml"
)

foreach ($Item in $Items) {
    if (Test-Path $Item) {
        $Acl = Get-Acl $Item

        # We simulate the chattr +i by denying write/delete to everyone
        $Rule = New-Object System.Security.AccessControl.FileSystemAccessRule("Everyone", "Write, Delete", "Deny")

        if ($Unlock) {
            $Acl.RemoveAccessRuleAll($Rule) | Out-Null
            Set-ItemProperty $Item -Name IsReadOnly -Value $false -ErrorAction SilentlyContinue
            Write-Host "[*] Unlocked $Item"
        } else {
            $Acl.AddAccessRule($Rule)
            Set-ItemProperty $Item -Name IsReadOnly -Value $true -ErrorAction SilentlyContinue
            Write-Host "[*] Locked $Item (Immutability Enforced)"
        }

        try {
            Set-Acl $Item $Acl
        } catch {
            Write-Host "[!] Could not set ACL on $Item"
        }
    }
}
