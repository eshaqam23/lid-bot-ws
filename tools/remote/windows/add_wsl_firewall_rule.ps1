$log = Join-Path $PSScriptRoot 'add_lidbot_fw.log'
try {
    $wsl = '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}'
    Get-NetFirewallHyperVRule -Name 'LidBot-ROS2-DDS-from-Pi' -ErrorAction SilentlyContinue | Remove-NetFirewallHyperVRule
    New-NetFirewallHyperVRule -Name 'LidBot-ROS2-DDS-from-Pi' -DisplayName 'LidBot ROS2 DDS from Pi (100.64.83.52)' `
        -Direction Inbound -VMCreatorId $wsl -Protocol UDP -LocalPorts 7400-7500 `
        -RemoteAddresses 100.64.83.52 -Action Allow -ErrorAction Stop | Out-Null
    Get-NetFirewallHyperVRule -Name 'LidBot-ROS2-DDS-from-Pi' | Format-List Name,Direction,Action,Protocol,LocalPorts,RemoteAddresses | Out-String | Set-Content $log
    Add-Content $log 'RULE_OK'
} catch {
    Set-Content $log "ERR: $($_.Exception.Message)"
}
