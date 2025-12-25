# Environment Configuration Specification: WSL2 Docker & Minikube Setup

**Feature Branch**: `phase-iv`
**Created**: 2025-12-22
**Status**: Ready for Implementation
**Target**: WSL2 Ubuntu environment for Kubernetes development

## Current Environment Assessment

### System Information
- **OS**: Windows 10 Pro (Version 2009)
- **WSL2**: Ubuntu (6.6.87.2-microsoft-standard-WSL2)
- **Architecture**: x86_64
- **Docker**: Version 29.1.3 detected but service not running
- **Minikube**: Not installed or not configured
- **Memory**: Available physical memory confirmed
- **Virtualization**: Status unknown (needs verification)

### Identified Issues
1. **Docker Service**: Docker CLI available but daemon not running
2. **Minikube**: Not accessible in current WSL2 environment
3. **WSL2 Integration**: Docker Desktop WSL2 integration not configured
4. **Kubernetes Tools**: kubectl and Helm CLI not available
5. **Resource Allocation**: System resources not yet allocated for Kubernetes

## Environment Setup Goals

### Primary Objectives
1. **Docker Integration**: Configure Docker Desktop with WSL2 backend
2. **Minikube Installation**: Install and configure Minikube with proper drivers
3. **Kubernetes Tools**: Install kubectl and Helm CLI
4. **Resource Optimization**: Allocate sufficient resources for cluster operation
5. **Service Integration**: Ensure seamless integration between WSL2, Docker, and Kubernetes

### Success Criteria
- Docker daemon running within WSL2 environment
- Minikube cluster operational with recommended resource allocation
- All Kubernetes CLI tools (kubectl, helm) functional
- Container images buildable and deployable
- TODO Evolution application deployable to Minikube

## Technical Requirements

### System Requirements
- **CPU**: 4+ cores recommended for Minikube
- **Memory**: 8GB+ RAM allocated to WSL2
- **Storage**: 20GB+ free disk space
- **Virtualization**: BIOS virtualization enabled
- **Network**: Internet connectivity for image downloads

### Software Components
1. **Docker Desktop** v4.30+ with WSL2 backend
2. **Minikube** v1.37+ with Docker driver
3. **kubectl** v1.29+ compatible with Minikube
4. **Helm CLI** v3.15+ for package management
5. **WSL2** Ubuntu 20.04+ with proper configuration

### Configuration Requirements
- WSL2 integration enabled in Docker Desktop
- Docker daemon accessible from WSL2
- Minikube using Docker driver for optimal performance
- Proper resource limits configured for Minikube
- Kubernetes tools configured and authenticated

## Environment Setup Architecture

### Component Integration Flow
```
Windows Host
├── Docker Desktop (WSL2 Backend)
│   ├── Docker Daemon (running in WSL2)
│   └── Docker CLI (accessible from WSL2)
├── WSL2 Ubuntu Environment
│   ├── Minikube (Docker Driver)
│   │   ├── Kubernetes Cluster
│   │   ├── kubectl (configured)
│   │   └── helm (installed)
│   └── TODO Evolution Application
│       ├── Source Code
│       ├── Container Images
│       └── Deployment Scripts
```

### Network Configuration
- **Docker Network**: Bridge network for container communication
- **Minikube Network**: Cluster network with service discovery
- **Host Integration**: Port forwarding for external access
- **DNS Resolution**: Kubernetes DNS and external DNS working

## Setup Procedure Specification

### Phase 1: Docker Desktop Configuration
1. **Verify Docker Desktop Installation**
   - Check Windows Docker Desktop version
   - Verify WSL2 feature enabled in Windows
   - Confirm Docker Desktop is running

2. **Configure WSL2 Integration**
   - Enable WSL2 integration in Docker Desktop
   - Select Ubuntu distribution for integration
   - Restart Docker Desktop to apply changes

3. **Verify Docker Functionality**
   - Test Docker CLI from WSL2
   - Verify Docker daemon connectivity
   - Test basic container operations

### Phase 2: Minikube Installation
1. **Install Minikube Binary**
   - Download latest Minikube release
   - Install to /usr/local/bin directory
   - Set executable permissions

2. **Configure Minikube Profile**
   - Create Minikube profile with Docker driver
   - Allocate resources (4 CPUs, 8GB RAM, 20GB disk)
   - Configure addons (ingress, metrics-server)

3. **Start Minikube Cluster**
   - Initialize cluster with Docker driver
   - Verify cluster status and connectivity
   - Test basic Kubernetes operations

### Phase 3: Kubernetes Tools Setup
1. **Install kubectl**
   - Download kubectl binary
   - Install to system PATH
   - Configure cluster access

2. **Install Helm CLI**
   - Download Helm binary
   - Install to system PATH
   - Verify installation and functionality

3. **Validate Tool Integration**
   - Test kubectl cluster access
   - Verify Helm client version
   - Test basic Helm operations

### Phase 4: Environment Validation
1. **Docker Validation**
   - Test Docker build operations
   - Verify Docker registry access
   - Test container lifecycle management

2. **Minikube Validation**
   - Verify cluster resource allocation
   - Test pod deployment and scheduling
   - Validate service and networking

3. **Integration Testing**
   - Build TODO Evolution containers
   - Deploy to Minikube cluster
   - Verify application functionality

## Troubleshooting Guide

### Common Issues and Solutions

#### Docker Desktop Issues
**Issue**: Docker daemon not accessible from WSL2
**Solution**:
- Restart Docker Desktop with WSL2 integration enabled
- Check Windows WSL2 feature is enabled
- Verify Ubuntu distribution is selected in Docker Desktop settings

**Issue**: Docker command timeouts
**Solution**:
- Check WSL2 resource allocation in Windows
- Restart WSL2 service: `wsl --shutdown` then restart
- Verify Docker Desktop service status

#### Minikube Issues
**Issue**: Minikube fails to start with Docker driver
**Solution**:
- Verify Docker daemon is running: `docker info`
- Check Docker Desktop WSL2 integration
- Restart Docker service and retry Minikube start

**Issue**: Insufficient resources for Minikube
**Solution**:
- Increase WSL2 memory allocation in Windows
- Close unnecessary applications
- Restart Minikube with higher resource limits

#### Kubernetes Tools Issues
**Issue**: kubectl cannot connect to cluster
**Solution**:
- Verify Minikube is running: `minikube status`
- Check kubectl configuration: `kubectl config current-context`
- Reconfigure kubectl: `minikube update-context`

**Issue**: Helm cannot find charts
**Solution**:
- Check Helm version compatibility
- Verify chart paths are correct
- Add stable repository if needed

### Diagnostic Commands

#### Docker Diagnostics
```bash
# Check Docker status
docker info
docker version
docker ps

# Check Docker Desktop integration
docker context ls
docker run hello-world
```

#### Minikube Diagnostics
```bash
# Check Minikube status
minikube status
minikube profile list

# Check cluster resources
minikube node list
kubectl top nodes
```

#### Kubernetes Diagnostics
```bash
# Check cluster connectivity
kubectl cluster-info
kubectl get nodes
kubectl get pods -A

# Check tool versions
kubectl version --client
helm version
```

## Validation Checklist

### Pre-Setup Validation
- [ ] Windows 10 Pro with WSL2 feature enabled
- [ ] Docker Desktop installed (v4.30+)
- [ ] Ubuntu WSL2 distribution installed
- [ ] Sufficient system resources (8GB+ RAM, 4+ CPUs)
- [ ] Administrative privileges for software installation

### Post-Setup Validation
- [ ] Docker daemon running in WSL2
- [ ] Docker CLI functional from WSL2
- [ ] Minikube installed and configured
- [ ] Minikube cluster operational
- [ ] kubectl installed and connected
- [ ] Helm CLI installed and functional
- [ ] TODO Evolution containers buildable
- [ ] Application deployable to cluster

### Integration Testing
- [ ] Build frontend container successfully
- [ ] Build backend container successfully
- [ ] Build MCP server container successfully
- [ ] Deploy all services to Minikube
- [ ] Verify pod startup and health status
- [ ] Test service accessibility
- [ ] Validate application functionality

## Performance Optimization

### Resource Allocation
- **Minikube Memory**: 8GB allocated
- **Minikube CPUs**: 4 cores allocated
- **Minikube Storage**: 20GB allocated
- **WSL2 Memory**: Dynamic allocation with 8GB limit
- **Docker Resources**: Default settings with WSL2 optimization

### Network Optimization
- Use Docker driver for Minikube (best WSL2 performance)
- Enable Docker Desktop WSL2 integration
- Configure proper DNS resolution
- Optimize image pull and caching strategies

### Storage Optimization
- Use Docker overlay2 storage driver
- Enable Minikube persistent volumes
- Optimize container layer caching
- Regular cleanup of unused images and containers

## Security Considerations

### Docker Security
- Run Docker Desktop with user permissions
- Use non-root containers where possible
- Enable content trust for image verification
- Regular security updates for Docker Desktop

### Kubernetes Security
- Enable Minikube security addons
- Configure proper RBAC permissions
- Use network policies for cluster isolation
- Regular security scanning of container images

### WSL2 Security
- Keep Ubuntu packages updated
- Use secure authentication methods
- Configure proper file permissions
- Enable firewall rules as needed

## References and Resources

### Official Documentation
- [Docker Desktop WSL 2 backend](https://docs.docker.com/desktop/features/wsl/)
- [Minikube WSL2 Tutorial](https://minikube.sigs.k8s.io/docs/tutorials/wsl_docker_driver/)
- [kubectl Installation Guide](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [Helm Installation Guide](https://helm.sh/docs/intro/install/)

### Setup Tutorials
- [WSL2 Docker Desktop Setup 2025](https://blog.csdn.net/weixin_48011951/article/details/155649814)
- [Minikube Windows 11 WSL2 Setup](https://harryhiyoshi.hashnode.dev/1-a-create-environment-install-minikube-in-windows-11-wsl20-ubuntu2204)
- [Kubernetes First Cluster Guide](https://medium.com/@marekczarnecki_50908/your-first-cluster-installing-minikube-and-helm-c2209b3f3cdc)

### Troubleshooting Resources
- [Docker Desktop Issues](https://forums.docker.com/)
- [Minikube Troubleshooting](https://minikube.sigs.k8s.io/docs/handbook/troubleshooting/)
- [Kubernetes Documentation](https://kubernetes.io/docs/home/)

This specification provides a comprehensive framework for configuring a WSL2 Ubuntu environment with Docker Desktop and Minikube for Kubernetes development, specifically tailored for the TODO Evolution application deployment requirements.