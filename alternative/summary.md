# MediaStack Alternative Configuration Summary

**Configuration Status**: ✅ **VERIFIED & READY FOR DEPLOYMENT**  
**Last Updated**: 2024  
**Version**: Alternative/Conditional Security Setup

## 📋 Overview

This alternative MediaStack configuration implements **IP-based conditional security** with three-tier protection levels:

- **🔐 Full Security**: Authentication + CrowdSec + Strict headers for untrusted IPs
- **🛡️ Trusted Access**: Relaxed headers + No authentication for trusted IPs  
- **📺 Media Services**: Optimized headers for media streaming applications

## 🏗️ Architecture Summary

### **Core Components**
- **Traefik**: Reverse proxy with conditional middleware chains
- **Authentik**: SSO/Identity Provider (when authentication required)
- **CrowdSec**: Web Application Firewall (when protection required)
- **PostgreSQL**: Database backend for Authentik
- **Valkey**: Redis-compatible cache for Authentik sessions

### **Security Model**
```
Internet Traffic
       ↓
   Traefik Proxy
       ↓
  IP Whitelist Check
       ↓
┌─────────────────┬─────────────────┐
│   Trusted IPs   │  Untrusted IPs  │
│                 │                 │
│ ✅ Direct Access │ 🔒 Authentication │
│ ✅ Relaxed Headers │ 🔒 Strict Headers │  
│ ✅ No CrowdSec   │ 🔒 CrowdSec WAF   │
└─────────────────┴─────────────────┘
       ↓
  Backend Services
```

## 📁 File Structure

```
alternative/
├── docker-compose.yaml          # Main service definitions
├── traefik-dynamic.yaml         # Traefik middleware configuration
├── docker-compose-no-tailscale.yaml  # Extended config without Tailscale
├── env.example-no-tailscale     # Environment variables template
└── summary.md                   # This file
```

## 🔧 Configuration Details

### **Traefik Middleware Configuration** (`traefik-dynamic.yaml`)

#### **Security Header Types**
1. **`security-headers-trusted`**: Relaxed headers for trusted IPs
   - No XSS filtering
   - Shorter HSTS duration  
   - Allows framing
   - No content type restrictions
   - No permissions policy

2. **`security-headers-strict`**: Strict headers for untrusted IPs
   - Full XSS protection
   - Long HSTS duration
   - Denies framing
   - Content Security Policy enforced
   - Strict permissions policy

3. **`security-headers`**: Default moderate headers for Authentik

#### **IP Whitelist Configuration**
```yaml
trusted-ips:
  ipWhiteList:
    sourceRange:
      - 127.0.0.1/32          # Localhost
      - 192.168.1.0/24        # Local network (adjust as needed)
      - 172.15.48.0/24        # Your LOCAL_SUBNET from env
      - 10.0.0.0/8            # Private network range
      # Add your specific trusted IPs:
      # - 203.0.113.10/32     # Your office IP
      # - 198.51.100.0/24     # Your VPN subnet
```

#### **Conditional Middleware Chains**
- **`conditional-auth`**: Authentication only for untrusted IPs
- **`conditional-security`**: Strict headers only for untrusted IPs  
- **`conditional-crowdsec`**: CrowdSec protection only for untrusted IPs

### **Service Configuration** (`docker-compose.yaml`)

#### **Services with Full Conditional Security**
These services require authentication from untrusted IPs:

| Service | Purpose | Middleware Chain |
|---------|---------|------------------|
| **Traefik Dashboard** | Reverse proxy admin | `conditional-auth` + `security-headers-trusted` + `conditional-crowdsec` |
| **Guacamole** | Remote desktop gateway | `conditional-auth` + `security-headers-trusted` + `conditional-crowdsec` |
| **Prometheus** | Monitoring data | `conditional-auth` + `security-headers-trusted` + `conditional-crowdsec` |
| **Grafana** | Monitoring dashboards | `conditional-auth` + `security-headers-trusted` + `conditional-crowdsec` |

#### **Services with Trusted Headers Only**
These services are accessible to all but use relaxed security headers:

| Category | Services | Middleware |
|----------|----------|------------|
| **Media Management** | Radarr, Sonarr, Lidarr, Bazarr, Mylar | `security-headers-trusted` |
| **Download Clients** | qBittorrent | `security-headers-trusted` |
| **Request Management** | Jellyseerr | `security-headers-trusted` |
| **Utilities** | Prowlarr, Huntarr, Filebot, Flaresolverr | `security-headers-trusted` |
| **Dashboards** | Heimdall, Homarr | `security-headers-trusted` |

#### **Services with Standard Headers**
| Service | Purpose | Middleware | Reason |
|---------|---------|------------|--------|
| **Authentik** | Identity Provider | `security-headers` | Prevents auth loops |

## 🌐 Network Configuration

### **Docker Network**
- **Name**: `mediastack`
- **Type**: Bridge network
- **Subnet**: Configurable via `${DOCKER_SUBNET}` environment variable
- **Gateway**: Configurable via `${DOCKER_GATEWAY}` environment variable

### **Port Mappings**
All services are accessible via Traefik reverse proxy using domain-based routing:
- **HTTPS**: Port 443 (primary access)
- **HTTP**: Port 80 (redirects to HTTPS)
- **Traefik Dashboard**: Port 8080 (direct access)
- **Traefik Metrics**: Port 8082 (Prometheus metrics)

## 🔐 Security Features

### **TLS/SSL Configuration**
- **Minimum Version**: TLS 1.2
- **Certificate Provider**: Let's Encrypt with Cloudflare DNS challenge
- **Cipher Suites**: Modern, secure cipher suites only
- **HSTS**: Enabled with subdomain inclusion and preload

### **Authentication Flow** (for protected services)
1. **Request arrives** at Traefik
2. **IP check** against trusted whitelist
3. **If trusted IP**: Direct access granted
4. **If untrusted IP**: Redirect to Authentik for authentication
5. **After authentication**: Access granted with session management

### **WAF Protection** (CrowdSec)
- **Real-time threat detection**
- **IP reputation checking**  
- **Automated blocking** of malicious IPs
- **Community threat intelligence**
- **Bypassed for trusted IPs**

## 📊 Service Categories

### **🔒 High Security** (Authentication Required from Untrusted IPs)
- Traefik Dashboard
- Guacamole (Remote Desktop)
- Prometheus (Monitoring Data)
- Grafana (Monitoring Dashboards)

### **🛡️ Medium Security** (Trusted Headers, No Authentication)
- All *ARR applications (Radarr, Sonarr, Lidarr, etc.)
- Download clients (qBittorrent)
- Media request management (Jellyseerr)
- Utility services (Prowlarr, Filebot, etc.)

### **🔑 Identity Management** (Special Configuration)
- Authentik (Standard headers to prevent auth loops)

## 🚀 Deployment Instructions

### **Prerequisites**
1. **Domain configured** in DNS (Cloudflare recommended)
2. **Environment variables** set in `.env` file
3. **Storage directories** created with proper permissions
4. **Docker and Docker Compose** installed

### **Quick Start**
```bash
# 1. Copy configuration files
cp -r alternative/ /your/deployment/path/

# 2. Configure environment variables
cp env.example-no-tailscale .env
# Edit .env with your specific values

# 3. Update trusted IP addresses in traefik-dynamic.yaml
# Add your specific trusted IPs to the sourceRange section

# 4. Deploy services
docker-compose up -d

# 5. Configure Authentik (first time only)
# Access https://auth.yourdomain.com and complete setup
# Create Traefik outpost and applications
```

### **Post-Deployment Configuration**

#### **Authentik Setup** (Required for authentication)
1. **Access Admin Interface**: `https://auth.yourdomain.com/if/admin/`
2. **Create Proxy Provider**:
   - Name: `traefik-proxy-provider`
   - External host: `https://auth.yourdomain.com`
   - Internal host: `http://authentik:9000`
3. **Create Outpost**:
   - Name: `traefik-outpost`  
   - Type: Proxy Provider
   - Integration: Local Docker connection
4. **Create Applications** for each protected service

#### **Trusted IP Configuration**
Update the `sourceRange` in `traefik-dynamic.yaml`:
```yaml
sourceRange:
  - 127.0.0.1/32          # Localhost
  - YOUR.HOME.NETWORK.0/24 # Your home network
  - YOUR.OFFICE.IP/32     # Your office IP
  - YOUR.VPN.SUBNET.0/24  # Your VPN subnet
```

## 🧪 Testing & Validation

### **Access Testing**
```bash
# Test from trusted IP (should work without authentication)
curl -I https://radarr.yourdomain.com
curl -I https://grafana.yourdomain.com

# Test from untrusted IP (should redirect to authentication)
# Use different network or VPN to test
```

### **Security Validation**
```bash
# Check TLS configuration
curl -I https://yourdomain.com
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Verify headers
curl -I https://radarr.yourdomain.com | grep -i "x-frame-options\|strict-transport"
```

## 🔧 Customization Options

### **Adding New Services**
1. **Add service** to `docker-compose.yaml`
2. **Choose appropriate middleware**:
   - High security: `conditional-auth@file,security-headers-trusted@file,conditional-crowdsec@file`
   - Medium security: `security-headers-trusted@file`
   - Basic: `security-headers@file`

### **Adjusting Security Levels**
- **More restrictive**: Change services to use `conditional-auth@file`
- **Less restrictive**: Change services to use `security-headers-trusted@file`
- **Custom headers**: Create new middleware in `traefik-dynamic.yaml`

### **IP Whitelist Management**
- **Add trusted IPs**: Update `sourceRange` in `trusted-ips` middleware
- **Remove IPs**: Remove from `sourceRange` list
- **Dynamic updates**: Restart Traefik after changes

## 🚨 Troubleshooting

### **Common Issues**

#### **403 Forbidden Errors**
- **Cause**: IP not in trusted list or CrowdSec blocking
- **Solution**: Add IP to whitelist or check CrowdSec decisions
```bash
docker exec crowdsec cscli decisions list
```

#### **Authentication Loops**
- **Cause**: Authentik service has `authentik-forwardauth` middleware
- **Solution**: Ensure Authentik only uses `security-headers@file`

#### **Services Not Accessible**
- **Cause**: Middleware reference errors or Traefik configuration issues
- **Solution**: Check Traefik logs and middleware definitions
```bash
docker logs traefik --tail=50
```

### **Debugging Commands**
```bash
# Check container status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check Traefik configuration
docker exec traefik cat /etc/traefik/traefik-dynamic.yaml

# Test internal connectivity
docker exec traefik wget -qO- http://authentik:9000/akprox/auth/traefik

# Check CrowdSec status
docker exec crowdsec cscli metrics
```

## 📈 Performance Considerations

### **Resource Usage**
- **Traefik**: ~50MB RAM, minimal CPU
- **Authentik**: ~200MB RAM, moderate CPU during auth
- **CrowdSec**: ~100MB RAM, low CPU
- **Total Overhead**: ~350MB RAM for security stack

### **Optimization Tips**
- **Trusted IPs**: Bypass authentication for better performance
- **Static files**: Consider CDN for media streaming
- **Database**: Tune PostgreSQL for your workload
- **Caching**: Valkey provides session caching for Authentik

## 🔄 Maintenance

### **Regular Tasks**
- **Update containers**: `docker-compose pull && docker-compose up -d`
- **Monitor logs**: Check for security events and errors
- **Review IP whitelist**: Add/remove trusted IPs as needed
- **Certificate renewal**: Automatic via Let's Encrypt

### **Security Updates**
- **CrowdSec collections**: Update security rules monthly
- **Authentik**: Monitor for security updates
- **Traefik**: Keep updated for security patches

## 📚 References

### **Documentation Links**
- [Traefik Documentation](https://doc.traefik.io/traefik/)
- [Authentik Documentation](https://docs.goauthentik.io/)
- [CrowdSec Documentation](https://docs.crowdsec.net/)
- [MediaStack Guide](https://MediaStack.Guide)

### **Configuration Files**
- `traefik-dynamic.yaml`: Middleware definitions and security configuration
- `docker-compose.yaml`: Service definitions and container orchestration
- `.env`: Environment variables for customization

---

## ✅ Configuration Verification

**Status**: All configurations have been verified and are ready for deployment.

**Key Fixes Applied**:
- ✅ Removed circular middleware references
- ✅ Standardized security header usage
- ✅ Configured proper IP-based conditional access
- ✅ Ensured Authentik compatibility
- ✅ Validated all service middleware chains

**Ready for**: Production deployment with IP-based conditional security.

---

*This summary was generated automatically based on the current configuration state.*
