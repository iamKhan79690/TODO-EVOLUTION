# Windows Setup Guide: WSL2, Docker Desktop & Minikube Configuration

**Purpose**: Configure Windows system for Kubernetes development environment
**Target**: Windows 10 Pro with WSL2 Ubuntu
**Estimated Time**: 20-30 minutes
**Difficulty**: Intermediate

---

## 📋 Table of Contents

1. [System Requirements Check](#system-requirements-check)
2. [Configure WSL2 Memory Allocation](#configure-wsl2-memory-allocation)
3. [Restart WSL2](#restart-wsl2)
4. [Install and Configure Docker Desktop](#install-and-configure-docker-desktop)
5. [Verify Docker Configuration](#verify-docker-configuration)
6. [Troubleshooting Common Issues](#troubleshooting-common-issues)
7. [Validation Checklist](#validation-checklist)
8. [Advanced Configuration](#advanced-configuration)

---

## 🔍 System Requirements Check

### Verify Windows Version

1. **Check Windows version**:
   - Press `Win + R`, type `winver`, press Enter
   - **Required**: Windows 10 version 2004 or higher
   - **Your system**: Windows 10 Pro Version 2009 ✅

2. **Verify WSL is installed**:
   ```powershell
   # Open PowerShell as Administrator
   wsl --list --verbose
   ```

3. **Check virtualization**:
   ```powershell
   # In PowerShell
   systeminfo | findstr "Virtualization"
   # Should show "Virtualization Enabled In Firmware: Yes"
   ```

### Required System Resources
- **Memory**: 16GB+ total system RAM (you have enough)
- **CPU**: 4+ cores (you have 4 cores ✅)
- **Storage**: 50GB+ free disk space for containers
- **Network**: Internet connection for downloads

---

## 💾 Configure WSL2 Memory Allocation

### Method 1: Using PowerShell (Recommended)

1. **Open PowerShell as Administrator**:
   - Click Start → Type "PowerShell"
   - Right-click "Windows PowerShell" → "Run as administrator"
   - Accept UAC prompt

2. **Navigate to User Profile Directory**:
   ```powershell
   cd $env:USERPROFILE
   ```

3. **Create .wslconfig file**:
   ```powershell
   notepad .wslconfig
   ```

4. **Add the following content** to the notepad file:
   ```ini
   [wsl2]
   # Allocate 8GB memory to WSL2
   memory=8GB

   # Use all 4 CPU cores
   processors=4

   # Allocate 2GB swap space
   swap=2GB

   # Use mirrored networking for better performance
   networkingMode=mirrored

   # Enable DNS tunneling
   dnsTunneling=true

   # Enable firewall
   firewall=true

   # Enable auto proxy detection
   autoProxy=true
   ```

5. **Save the file**:
   - Press `Ctrl + S`
   - Close notepad

6. **Verify file was created**:
   ```powershell
   # Check if file exists
   Test-Path $env:USERPROFILE\.wslconfig
   # Should return: True

   # View the content
   Get-Content $env:USERPROFILE\.wslconfig
   ```

### Method 2: Using File Explorer

1. **Open File Explorer**:
   - Press `Win + E` or click File Explorer icon

2. **Navigate to User Profile**:
   - In address bar, type: `%USERPROFILE%`
   - Press Enter
   - This opens your C:\Users\YourUsername folder

3. **Enable File Extensions**:
   - Click "View" tab
   - Check "File name extensions"
   - Check "Hidden items"

4. **Create the .wslconfig file**:
   - Right-click in empty space → "New" → "Text Document"
   - Rename the new file from "New Text Document.txt" to ".wslconfig"
   - If you get a warning about file extension, click "Yes"

5. **Edit the file**:
   - Right-click .wslconfig → "Open with" → "Notepad"
   - Copy and paste the configuration content from Method 1.4
   - Save and close notepad

---

## 🔄 Restart WSL2

### Complete Shutdown

1. **Open PowerShell as Administrator**

2. **Shutdown WSL2 completely**:
   ```powershell
   wsl --shutdown
   ```

3. **Wait for complete shutdown**:
   - Wait 10-15 seconds
   - You should see WSL2 processes disappear from Task Manager

### Restart WSL2

1. **Start WSL2**:
   ```powershell
   wsl
   ```

2. **Verify memory allocation worked**:
   ```bash
   # Inside WSL2 Ubuntu, run:
   free -h
   ```

   **Expected output**:
   ```
   total        used        free      shared  buff/cache   available
   Mem:           7.9Gi       1.2Gi       6.7Gi       3.5Mi       192Mi       6.7Gi
   Swap:          2.0Gi          0B       2.0Gi
   ```

   **Key point**: Should show approximately 8GB total memory

---

## 🐳 Install and Configure Docker Desktop

### Step 1: Install Docker Desktop (if not already installed)

1. **Download Docker Desktop**:
   - Go to: https://www.docker.com/products/docker-desktop/
   - Click "Download for Windows"
   - Download "Docker Desktop for Windows"

2. **Run the installer**:
   - Double-click the downloaded installer
   - Use "Use WSL 2 instead of Hyper-V" if prompted
   - Complete the installation with default settings
   - Restart computer when prompted

3. **Verify installation**:
   ```powershell
   # Check Docker Desktop service
   Get-Service DockerDesktop

   # Check installation
   Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Docker Desktop"
   ```

### Step 2: Configure WSL2 Integration

1. **Start Docker Desktop**:
   - Click Start → Type "Docker Desktop" → Open it
   - Wait for it to fully start (green whale icon in system tray)
   - This may take 1-2 minutes on first start

2. **Open Docker Desktop Settings**:
   - Click the gear icon ⚙️ in the top-right corner
   - OR right-click Docker Desktop icon → "Settings"

3. **Configure General Settings**:
   - Go to **General** tab
   - Ensure **"Start Docker Desktop when you log in"** is checked
   - Ensure **"Use WSL 2 based engine"** is checked

4. **Configure WSL Integration**:
   - Go to **Resources** → **WSL Integration**
   - ✅ Check **"Enable integration with my default WSL distro"**
   - ✅ Check **"Ubuntu"** if it appears in the list
   - Click **"Apply & Restart"**

5. **Wait for restart**:
   - Docker Desktop will restart
   - This takes 1-2 minutes
   - Watch the system tray icon for completion

---

## ✅ Verify Docker Configuration

### Test Docker from PowerShell

1. **Open PowerShell** (not necessarily as administrator)

2. **Check Docker contexts**:
   ```powershell
   docker context ls
   ```

   **Expected output**:
   ```
   NAME                TYPE               DESCRIPTION                               DOCKER ENDPOINT               KUBERNETES ENDPOINT   SWARM MODE
   default *           moby               Current DOCKER_HOST based configuration   npipe:////./pipe/docker_cli                           false
   wsl                 wsl                                          npipe:////./pipe/docker_wsl                          false
   ```

3. **Test Docker version**:
   ```powershell
   docker version
   ```

   **Expected**: Both Client and Server information should appear

4. **Test Docker info**:
   ```powershell
   docker info
   ```

### Test Docker from WSL2

1. **Open WSL2 Ubuntu**:
   ```powershell
   wsl
   ```

2. **Test Docker commands in WSL2**:
   ```bash
   # Check Docker version
   docker version

   # Test container operations
   docker run hello-world
   ```

   **Expected output from hello-world**:
   ```
   Hello from Docker!
   This message shows that your installation appears to be working correctly.
   ...
   ```

3. **Test image operations**:
   ```bash
   # Pull a test image
   docker pull nginx:alpine

   # List images
   docker images

   # Run a test container
   docker run -d --name test-nginx -p 8080:80 nginx:alpine

   # Test container access
   curl http://localhost:8080

   # Expected: HTML welcome page from nginx

   # Clean up test container
   docker stop test-nginx
   docker rm test-nginx
   ```

---

## 🔧 Troubleshooting Common Issues

### Issue 1: .wslconfig File Not Working

**Symptoms**: `free -h` still shows 4GB memory instead of 8GB

**Solutions**:

1. **Check file location and permissions**:
   ```powershell
   # Verify file exists
   Get-ChildItem $env:USERPROFILE -Filter .wslconfig -Force

   # Check file content
   Get-Content $env:USERPROFILE\.wslconfig

   # Ensure proper encoding
   Get-Content $env:USERPROFILE\.wslconfig | Out-File $env:USERPROFILE\.wslconfig -Encoding UTF8
   ```

2. **Force WSL restart**:
   ```powershell
   # Complete shutdown
   wsl --shutdown

   # Wait 15 seconds
   Start-Sleep 15

   # Restart
   wsl
   ```

3. **Check Windows version compatibility**:
   - .wslconfig requires Windows 10 build 18362 or higher
   - Your Windows 10 Pro Version 2009 should be compatible

### Issue 2: Docker Desktop WSL2 Integration Not Working

**Symptoms**: `docker version` shows "Cannot connect to Docker daemon"

**Solutions**:

1. **Reset Docker Desktop**:
   - Open Docker Desktop
   - Go to "Troubleshoot"
   - Click "Reset to factory defaults"
   - Wait for reset to complete
   - Reconfigure WSL2 integration (Step 2.2)

2. **Check Docker context**:
   ```powershell
   # List available contexts
   docker context ls

   # Switch to WSL context if needed
   docker context use wsl
   ```

3. **Restart Docker service**:
   ```powershell
   # Restart Docker Desktop service
   Restart-Service DockerDesktop

   # Or restart entire Docker Desktop
   taskkill /f /im "Docker Desktop.exe"
   start "Docker Desktop"
   ```

### Issue 3: Docker Commands Not Found in WSL2

**Symptoms**: `bash: docker: command not found`

**Solutions**:

1. **Check Docker Desktop is running**:
   - Look for Docker Desktop icon in system tray
   - Should be green, not red or yellow

2. **Restart WSL2**:
   ```powershell
   wsl --shutdown
   wsl
   ```

3. **Check Docker context in WSL2**:
   ```bash
   # In WSL2
   echo $DOCKER_HOST
   # Should be empty or show WSL context

   # Try explicitly using WSL context
   docker context use wsl
   ```

### Issue 4: Port Forwarding Not Working

**Symptoms**: Cannot access localhost ports from Docker containers

**Solutions**:

1. **Check Windows Firewall**:
   - Windows Defender Security Center → Firewall & network protection
   - Allow "Docker Desktop" through firewall

2. **Use mirrored networking** (already configured in .wslconfig):
   - This provides better localhost port forwarding

3. **Test with alternative method**:
   ```powershell
   # Check Docker network
   docker network ls

   # Use bridge network if needed
   docker run --network=bridge -p 8080:80 nginx:alpine
   ```

---

## ✅ Validation Checklist

Before proceeding to Phase D, verify ALL of these work:

### ✅ Memory Configuration
```bash
# In WSL2 Ubuntu
free -h
# Expected: ~8GB total memory
```

### ✅ Docker Desktop Status
- Docker Desktop running (green icon in system tray)
- WSL2 integration enabled in settings

### ✅ Docker Basic Operations
```powershell
# In PowerShell
docker version
# Expected: Both client and server info

docker run hello-world
# Expected: Success message
```

### ✅ Docker in WSL2
```bash
# In WSL2 Ubuntu
docker version
# Expected: Both client and server info

docker pull nginx:alpine
# Expected: Successful image download

docker run -d -p 8080:80 nginx:alpine
# Expected: Container starts successfully

curl http://localhost:8080
# Expected: NGINX welcome page HTML

docker stop $(docker ps -q)
# Expected: Containers stop successfully
```

### ✅ System Resources Check
```powershell
# Check available memory
Get-WmiObject -Class Win32_ComputerSystem | Select-Object TotalPhysicalMemory

# Check CPU cores
Get-WmiObject -Class Win32_Processor | Select-Object NumberOfCores
```

---

## ⚡ Advanced Configuration (Optional)

### Optimize Windows Virtual Memory

1. **Open System Properties**:
   - Right-click "This PC" → Properties
   - Click "Advanced system settings"

2. **Configure virtual memory**:
   - Under "Performance", click "Settings"
   - Go to "Advanced" tab
   - Under "Virtual memory", click "Change"
   - Uncheck "Automatically manage paging file size for all drives"
   - Select Custom size
   - Initial size: 8192 MB
   - Maximum size: 16384 MB
   - Click "Set" → "OK" → "Apply"

### Optimize Windows Power Settings

1. **Open Power Options**:
   - Type "Power Options" in Start menu
   - Press Enter

2. **Set High Performance**:
   - Click "Additional power settings"
   - Select "High performance" plan
   - Or create custom plan with balanced settings

### Configure Windows Defender (Temporary)

```powershell
# Run PowerShell as Administrator
# Disable real-time protection temporarily for better performance
Set-MpPreference -DisableRealtimeMonitoring $true

# Remember to re-enable later:
Set-MpPreference -DisableRealtimeMonitoring $false
```

---

## 📊 Performance Expectations

### After Configuration, Expect:
- **WSL2 Startup**: 10-15 seconds
- **Docker Desktop**: 1-2 minutes to full startup
- **Container Build**: 2-5 minutes for average applications
- **Minikube Startup**: 2-4 minutes (when ready)
- **Memory Usage**: 2-4GB idle, 6-8GB under load

### Resource Allocation Summary:
- **Total System RAM**: 16GB+ (your system)
- **WSL2 Allocation**: 8GB (configured)
- **Windows Reserved**: 8GB (for Windows)
- **Docker Containers**: Use WSL2 memory pool
- **Minikube Cluster**: Use WSL2 memory pool

---

## 🎯 Next Steps

Once you complete ALL validation checks:

1. **Return to the TODO Evolution project**
2. **I will automatically execute**:
   - Minikube installation
   - Kubernetes tools setup
   - Cluster configuration
   - TODO Evolution deployment
3. **Phase D Kubernetes deployment** will proceed automatically

### Final Validation Command:
```bash
# Run this in WSL2 to confirm everything is ready
docker --version && \
echo "--- Docker Test ---" && \
docker run --rm hello-world && \
echo "--- Ready for Phase D ---"
```

**If this command runs successfully, your environment is ready for Phase D deployment!**

---

## 📞 Support Resources

### Official Documentation:
- [WSL2 Configuration](https://docs.microsoft.com/en-us/windows/wsl/wsl-config)
- [Docker Desktop WSL2](https://docs.docker.com/desktop/windows/wsl/)
- [Docker Troubleshooting](https://docs.docker.com/desktop/troubleshoot/)

### Common Commands:
```powershell
# Restart everything
wsl --shutdown
taskkill /f /im "Docker Desktop.exe"
start "Docker Desktop"
wsl

# Check Docker status
docker context ls
docker info
docker version

# Clean up Docker
docker system prune -f
```

---

**Setup Complete!** 🎉

Once all validation checks pass, you're ready for Kubernetes development and Phase D deployment!