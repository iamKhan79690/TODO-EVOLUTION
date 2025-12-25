# Environment Setup Plan: WSL2 Docker & Minikube Configuration

**Created**: 2025-12-22
**Status**: Ready for Implementation
**Target**: Complete environment setup for Kubernetes development
**Estimated Duration**: 2-3 hours
**Priority**: P1 (Required for Phase D deployment)

## Executive Summary

This plan provides a step-by-step approach to configure the WSL2 Ubuntu environment with Docker Desktop and Minikube for Kubernetes development. The setup will enable local Kubernetes cluster deployment for the TODO Evolution application with proper resource allocation and tool integration.

## Current Environment Analysis

### System Status
- **Windows 10 Pro**: Version 2009 with WSL2 support
- **WSL2 Ubuntu**: Running (6.6.87.2-microsoft-standard-WSL2)
- **Docker CLI**: Version 29.1.3 available but daemon not running
- **Minikube**: Not installed or accessible
- **Kubernetes Tools**: Not installed (kubectl, helm)

### Critical Issues Identified
1. Docker Desktop WSL2 integration not configured
2. Minikube binary missing from system PATH
3. Kubernetes CLI tools not installed
4. Resource allocation not optimized for Kubernetes

## Implementation Strategy

### Approach Overview
1. **Sequential Setup**: Configure components in dependency order
2. **Validation at Each Step**: Verify each component before proceeding
3. **Rollback Capability**: Ability to undo changes if issues occur
4. **Documentation**: Record all configuration changes
5. **Testing**: Verify end-to-end functionality

### Success Criteria
- Docker daemon operational within WSL2
- Minikube cluster running with Docker driver
- kubectl and Helm CLI functional
- TODO Evolution application deployable
- All health checks passing

## Detailed Implementation Plan

### Phase 1: Docker Desktop Configuration (45 minutes)

#### Step 1.1: Verify Windows Prerequisites (10 minutes)
**Objective**: Ensure Windows environment supports Docker Desktop WSL2 integration

**Actions**:
```powershell
# Check Windows version
winver

# Verify WSL2 feature
dism.exe /online /get-features /format:table | findstr WSL

# Check virtualization status
systeminfo | findstr "Virtualization"
```

**Validation**:
- Windows 10 Pro version 2004+ confirmed
- WSL2 feature enabled
- Virtualization enabled in BIOS

**Rollback Plan**: Enable WSL2 feature via Windows Features if disabled

#### Step 1.2: Configure Docker Desktop WSL2 Integration (15 minutes)
**Objective**: Enable Docker daemon to run within WSL2 Ubuntu environment

**Actions**:
1. **Open Docker Desktop Settings**
   - Navigate to Settings > Resources > WSL Integration
   - Enable "Use the WSL 2 based engine"
   - Select Ubuntu distribution for integration
   - Apply settings and restart Docker Desktop

2. **Verify Integration**
```bash
# From WSL2 Ubuntu
docker context ls
docker version
docker info
```

**Validation**:
- Docker context shows "default" and "wsl" contexts
- Docker daemon accessible from WSL2
- Docker version information returned

**Rollback Plan**: Disable WSL2 integration, restart Docker Desktop

#### Step 1.3: Test Docker Functionality (20 minutes)
**Objective**: Verify complete Docker functionality in WSL2 environment

**Actions**:
```bash
# Test basic Docker operations
docker run hello-world
docker pull nginx:alpine
docker run -d -p 8080:80 --name test-nginx nginx:alpine
curl http://localhost:8080
docker stop test-nginx
docker rm test-nginx
```

**Validation**:
- Hello World container runs successfully
- Image pull operations work
- Container networking functional
- Container lifecycle management working

**Rollback Plan**: Restart Docker Desktop, verify WSL2 integration

### Phase 2: Minikube Installation and Configuration (60 minutes)

#### Step 2.1: Install Minikube Binary (15 minutes)
**Objective**: Install Minikube command-line tool for Kubernetes cluster management

**Actions**:
```bash
# Download latest Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
rm minikube-linux-amd64

# Verify installation
minikube version
```

**Validation**:
- Minikube binary accessible in PATH
- Version information displayed correctly

**Rollback Plan**: Remove Minikube binary from /usr/local/bin/

#### Step 2.2: Configure Minikube Profile (20 minutes)
**Objective**: Create Minikube profile with optimal resource allocation for TODO Evolution

**Actions**:
```bash
# Create profile with Docker driver
minikube profile create todo-evolution --driver=docker

# Configure resources
minikube profile todo-evolution --memory=8192 --cpus=4 --disk-size=20g

# Verify profile configuration
minikube profile list
```

**Validation**:
- Profile created successfully
- Resource allocation configured
- Profile appears in profile list

**Rollback Plan**: Delete profile: `minikube profile delete todo-evolution`

#### Step 2.3: Start Minikube Cluster (25 minutes)
**Objective**: Initialize Kubernetes cluster with Docker driver and required addons

**Actions**:
```bash
# Start Minikube with Docker driver
minikube start --profile=todo-evolution --driver=docker

# Enable required addons
minikube addons enable ingress --profile=todo-evolution
minikube addons enable metrics-server --profile=todo-evolution
minikube addons enable dashboard --profile=todo-evolution

# Verify cluster status
minikube status --profile=todo-evolution
kubectl cluster-info
```

**Validation**:
- Minikube cluster starts successfully
- All required addons enabled
- kubectl can connect to cluster
- Cluster nodes show Ready status

**Rollback Plan**: `minikube stop --profile=todo-evolution` then `minikube delete --profile=todo-evolution`

### Phase 3: Kubernetes Tools Installation (45 minutes)

#### Step 3.1: Install kubectl (15 minutes)
**Objective**: Install Kubernetes command-line tool for cluster management

**Actions**:
```bash
# Download kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl

# Configure kubectl for Minikube
minikube update-context --profile=todo-evolution

# Verify installation
kubectl version --client
kubectl config current-context
```

**Validation**:
- kubectl binary accessible in PATH
- Connected to Minikube cluster
- Version information displayed

**Rollback Plan**: Remove kubectl binary, reset kubectl configuration

#### Step 3.2: Install Helm CLI (15 minutes)
**Objective**: Install Helm package manager for Kubernetes applications

**Actions**:
```bash
# Download Helm
curl https://get.helm.sh/helm-v3.15.0-linux-amd64.tar.gz -o helm.tar.gz
tar -zxvf helm.tar.gz
sudo mv linux-amd64/helm /usr/local/bin/helm
rm -rf helm.tar.gz linux-amd64

# Verify installation
helm version
helm repo add stable https://charts.helm.sh/stable
helm repo update
```

**Validation**:
- Helm binary accessible in PATH
- Version information displayed
- Repository operations successful

**Rollback Plan**: Remove Helm binary, delete repository configurations

#### Step 3.3: Validate Kubernetes Tools (15 minutes)
**Objective**: Verify all Kubernetes tools are properly integrated and functional

**Actions**:
```bash
# Test kubectl operations
kubectl get nodes
kubectl get pods -A
kubectl get services -A

# Test Helm operations
helm search repo nginx
helm pull stable/nginx --untar

# Verify Minikube integration
minikube dashboard --url
minikube service list
```

**Validation**:
- kubectl commands return valid cluster information
- Helm repository operations work
- Minikube dashboard accessible
- Service listing functional

**Rollback Plan**: Reinstall problematic tool, verify integration steps

### Phase 4: Environment Validation and Testing (60 minutes)

#### Step 4.1: Docker-Minikube Integration Test (20 minutes)
**Objective**: Verify Docker and Minikube are properly integrated

**Actions**:
```bash
# Test Docker registry access from Minikube
docker pull nginx:alpine
minikube image load nginx:alpine

# Deploy test application
kubectl create deployment test-nginx --image=nginx:alpine
kubectl expose deployment test-nginx --port=80 --type=NodePort
kubectl get services

# Test application access
minikube service test-nginx --url
```

**Validation**:
- Docker images accessible to Minikube
- Test deployment successful
- Service accessible via Minikube

**Rollback Plan**: `kubectl delete deployment test-nginx` and `kubectl delete service test-nginx`

#### Step 4.2: Build TODO Evolution Containers (20 minutes)
**Objective**: Build all TODO Evolution container images and verify they work

**Actions**:
```bash
# Navigate to project directories
cd /mnt/d/Hackathon/TODO-Evolution

# Build frontend container
cd frontend
docker build -t todo-frontend:1.0.0 .
docker images todo-frontend

# Build backend container
cd ../backend
docker build -t todo-backend:1.0.0 .
docker images todo-backend

# Build MCP server container
cd ../mcp_server
docker build -t todo-mcp:1.0.0 .
docker images todo-mcp
```

**Validation**:
- All three containers build successfully
- Images appear in Docker registry
- No build errors or warnings

**Rollback Plan**: Remove built images, fix Dockerfile issues

#### Step 4.3: Deploy Test Application (20 minutes)
**Objective**: Deploy TODO Evolution application to Minikube and verify functionality

**Actions**:
```bash
# Load images into Minikube
minikube image load todo-frontend:1.0.0
minikube image load todo-backend:1.0.0
minikube image load todo-mcp:1.0.0

# Test basic deployment without Helm
kubectl create deployment todo-backend-test --image=todo-backend:1.0.0
kubectl get pods
kubectl logs deployment/todo-backend-test

# Clean up test deployment
kubectl delete deployment todo-backend-test
```

**Validation**:
- Images successfully loaded into Minikube
- Test deployment starts successfully
- Pod logs show application starting
- Cleanup operations work

**Rollback Plan**: Delete any failed deployments, remove problematic images

## Risk Assessment and Mitigation

### High-Risk Areas
1. **Docker Desktop WSL2 Integration**: Configuration issues can prevent Docker daemon access
   - **Mitigation**: Follow official Docker documentation, restart services as needed

2. **Minikube Resource Allocation**: Insufficient resources can cause cluster failures
   - **Mitigation**: Verify system resources before starting, monitor resource usage

3. **Network Configuration**: WSL2 networking can cause connectivity issues
   - **Mitigation**: Use Docker driver for Minikube, test network connectivity thoroughly

### Medium-Risk Areas
1. **Binary Installation**: Download/installation failures for kubectl and Helm
   - **Mitigation**: Use official download links, verify checksums

2. **Cluster Startup**: Minikube may fail to start with Docker driver
   - **Mitigation**: Check Docker daemon status, try alternative drivers if needed

### Low-Risk Areas
1. **Profile Configuration**: Resource allocation settings
   - **Mitigation**: Start with conservative resource limits

## Quality Assurance

### Validation Checkpoints
1. **After Docker Setup**: Docker daemon accessible, basic operations working
2. **After Minikube Installation**: Binary installed, cluster starting
3. **After Tool Installation**: kubectl and Helm functional
4. **After Integration Testing**: All components working together
5. **Final Validation**: TODO Evolution application deployable

### Success Metrics
- Docker daemon operational within 5 minutes of WSL2 integration
- Minikube cluster Ready status achieved within 10 minutes
- All Kubernetes CLI tools functional
- TODO Evolution containers build successfully
- Test deployment completes without errors

### Performance Benchmarks
- Container build time: < 2 minutes per service
- Minikube startup time: < 5 minutes
- kubectl command response time: < 2 seconds
- Helm chart rendering time: < 10 seconds

## Documentation and Knowledge Transfer

### Configuration Documentation
- Document all Docker Desktop settings
- Record Minikube profile configuration
- Save tool installation commands
- Create troubleshooting guide

### Environment Reset Procedures
- Docker Desktop reset steps
- Minikube profile deletion commands
- kubectl configuration reset
- Complete environment rebuild steps

### Best Practices
- Regular environment updates
- Image cleanup procedures
- Resource monitoring practices
- Security configuration guidelines

## Timeline and Milestones

### Phase 1: Docker Desktop Configuration (45 minutes)
- **Milestone 1**: WSL2 integration enabled (25 minutes)
- **Milestone 2**: Docker functionality verified (45 minutes)

### Phase 2: Minikube Installation (60 minutes)
- **Milestone 3**: Minikube binary installed (75 minutes)
- **Milestone 4**: Cluster operational (135 minutes)

### Phase 3: Kubernetes Tools Setup (45 minutes)
- **Milestone 5**: kubectl and Helm installed (180 minutes)

### Phase 4: Validation and Testing (60 minutes)
- **Milestone 6**: Integration tests passing (240 minutes)

**Total Estimated Duration**: 4 hours (including buffer time)

## Post-Setup Activities

### Environment Optimization
- Configure aliases for common commands
- Set up shell completion for kubectl and Helm
- Configure backup procedures for Minikube
- Set up monitoring and alerting

### Team Enablement
- Create environment setup documentation
- Provide troubleshooting guides
- Conduct environment walkthrough
- Establish maintenance procedures

### Ongoing Maintenance
- Regular Docker Desktop updates
- Minikube version upgrades
- Kubernetes tool updates
- Performance monitoring and optimization

This plan provides a comprehensive roadmap for configuring the development environment with all necessary tools and configurations for Kubernetes deployment of the TODO Evolution application.