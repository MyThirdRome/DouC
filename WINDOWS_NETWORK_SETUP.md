# Windows Network Setup for DOU Blockchain

## Firewall Configuration

### Allow Python Through Windows Firewall
1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Click "Inbound Rules"
4. Click "New Rule"
5. Select "Program"
6. Browse to Python executable (e.g., `C:\Users\YourUsername\AppData\Local\Programs\Python\Python39\python.exe`)
7. Allow the connection for Domain, Private, and Public networks
8. Name the rule "Python Network Access"

## Network Troubleshooting

### Check Open Ports
```powershell
# Check if ports are open
netstat -ano | findstr :5000
netstat -ano | findstr :5001
```

### Disable Windows Firewall (Temporary Testing)
```powershell
# Run as Administrator
netsh advfirewall set allprofiles state off
```

### Re-enable Firewall
```powershell
# Run as Administrator
netsh advfirewall set allprofiles state on
```

## IP Address Configuration

### Find Your IP Address
```powershell
ipconfig
```
Look for:
- IPv4 Address under Wi-Fi or Ethernet adapter
- Typically starts with 192.168.x.x or 10.0.x.x

### Set Environment Variables
```powershell
# Persistent setting
[System.Environment]::SetEnvironmentVariable("DOU_VALIDATOR_HOST", "192.168.1.100:5001", "User")
[System.Environment]::SetEnvironmentVariable("DOU_RELAY_HOST", "192.168.1.100:5000", "User")

# Temporary setting (current session)
$env:DOU_VALIDATOR_HOST = "192.168.1.100:5001"
$env:DOU_RELAY_HOST = "192.168.1.100:5000"
```

## Common Issues
- Antivirus blocking network access
- Firewall preventing connections
- Incorrect IP address
- Python not in system PATH

## Recommended Tools
- [Wireshark](https://www.wireshark.org/) for network debugging
- [PuTTY](https://www.putty.org/) for SSH and port testing
