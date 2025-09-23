# Fail2Ban Setup Instructions for FastAPI Authentication

## Overview
This setup protects your FastAPI authentication endpoints from brute force attacks by monitoring access logs and automatically banning IP addresses that make too many failed login attempts.

## Installation

### 1. Install Fail2Ban
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install fail2ban

# CentOS/RHEL
sudo yum install epel-release
sudo yum install fail2ban

# macOS (via Homebrew)
brew install fail2ban
```

### 2. Copy Configuration Files
```bash
# Copy the filter definition
sudo cp fail2ban/filter.d/fastapi-auth.conf /etc/fail2ban/filter.d/

# Copy the jail configuration
sudo cp fail2ban/jail.d/fastapi-auth.conf /etc/fail2ban/jail.d/
```

### 3. Configure Logging in FastAPI
Add this middleware to your FastAPI app to log authentication attempts:

```python
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/fastapi/access.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("fastapi-auth")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log authentication attempts
    if request.url.path in ["/login", "/register"]:
        logger.info(
            f"{request.client.host} - "
            f'"{request.method} {request.url.path}" '
            f"{response.status_code} - {process_time:.4f}s"
        )
    
    return response
```

### 4. Create Log Directory
```bash
sudo mkdir -p /var/log/fastapi
sudo chown www-data:www-data /var/log/fastapi  # Adjust user as needed
```

### 5. Start Fail2Ban
```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## Configuration Details

### Filter Configuration
- **Location**: `/etc/fail2ban/filter.d/fastapi-auth.conf`
- **Purpose**: Defines patterns to match failed authentication attempts
- **Triggers**: 401 responses for login, 400 responses for registration

### Jail Configuration
- **Location**: `/etc/fail2ban/jail.d/fastapi-auth.conf`
- **Settings**:
  - `maxretry = 5`: Ban after 5 failed attempts
  - `findtime = 600`: Within 10 minutes
  - `bantime = 3600`: Ban for 1 hour
  - `port = 8000`: Default FastAPI port

## Management Commands

### Check Fail2Ban Status
```bash
sudo fail2ban-client status
sudo fail2ban-client status fastapi-auth
```

### View Banned IPs
```bash
sudo fail2ban-client get fastapi-auth banip
```

### Unban an IP
```bash
sudo fail2ban-client set fastapi-auth unbanip <IP_ADDRESS>
```

### Reload Configuration
```bash
sudo fail2ban-client reload
```

### Test Filter
```bash
sudo fail2ban-regex /var/log/fastapi/access.log /etc/fail2ban/filter.d/fastapi-auth.conf
```

## Customization

### Adjust Ban Settings
Edit `/etc/fail2ban/jail.d/fastapi-auth.conf`:
- Increase `maxretry` for more lenient protection
- Decrease `bantime` for shorter bans
- Adjust `findtime` for different detection windows

### Add Email Notifications
Add to jail configuration:
```ini
action = iptables-multiport[name=fastapi-auth, port="8000", protocol=tcp]
         sendmail-whois[name=fastapi-auth, dest=admin@example.com]
```

### Whitelist IPs
Add trusted IPs to jail configuration:
```ini
ignoreip = 127.0.0.1/8 ::1 192.168.1.0/24
```

## Monitoring

### View Logs
```bash
# Fail2Ban logs
sudo tail -f /var/log/fail2ban.log

# FastAPI access logs
sudo tail -f /var/log/fastapi/access.log
```

### Check Ban Statistics
```bash
sudo fail2ban-client status fastapi-auth
```

## Production Recommendations

1. **Rate Limiting**: Combine with application-level rate limiting
2. **HTTPS**: Always use HTTPS in production
3. **Strong Passwords**: Enforce strong password policies
4. **Account Lockout**: Implement account lockout after multiple failures
5. **Monitoring**: Set up alerts for ban events
6. **Log Rotation**: Configure logrotate for access logs

## Troubleshooting

### Common Issues
1. **Log file permissions**: Ensure FastAPI can write to log directory
2. **Port mismatch**: Update port in jail config if using different port
3. **Log format**: Ensure log format matches filter regex
4. **Firewall rules**: Check if iptables rules are applied correctly

### Debug Commands
```bash
# Test filter against log file
sudo fail2ban-regex /var/log/fastapi/access.log /etc/fail2ban/filter.d/fastapi-auth.conf

# Check jail configuration
sudo fail2ban-client get fastapi-auth maxretry
sudo fail2ban-client get fastapi-auth bantime
sudo fail2ban-client get fastapi-auth findtime
```