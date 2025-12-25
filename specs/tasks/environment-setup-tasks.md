# Environment Setup Tasks: WSL2 Docker & Minikube Configuration

**Generated From**: `specs/plans/environment-setup-plan.md`
**Created**: 2025-12-22
**Total Tasks**: 12
**Estimated Duration**: 4 hours
**Priority**: P1 (Required for Phase D deployment)

## Task Summary

This task list breaks down the environment setup into concrete, actionable steps for configuring WSL2 Ubuntu with Docker Desktop and Minikube for Kubernetes development of the TODO Evolution application.

## Phase 1: Docker Desktop Configuration

### Task 1.1: Verify Windows Prerequisites
**Task ID**: ENV-001
**Description**: Verify Windows system meets requirements for Docker Desktop WSL2 integration
**Prerequisites**: Windows 10 Pro with administrative access
**Expected Outcome**: System confirmed compatible with Docker Desktop WSL2 integration
**Verification Method**:
- Run `winver` to confirm Windows version 2004+
- Verify WSL2 feature enabled via `dism.exe /online /get-features`
- Check virtualization enabled in BIOS/UEFI settings
- Confirm sufficient system resources (8GB+ RAM recommended)
**Estimated Time**: 10 minutes
**Dependencies**: None

### Task 1.2: Configure Docker Desktop WSL2 Integration
**Task ID**: ENV-002
**Description**: Enable Docker daemon to run within WSL2 Ubuntu environment for optimal performance
**Prerequisites**: ENV-001 completed, Docker Desktop installed
**Expected Outcome**: Docker daemon accessible and functional from WSL2 Ubuntu
**Verification Method**:
- Open Docker Desktop settings and enable WSL2 integration
- Select Ubuntu distribution in Docker Desktop settings
- Restart Docker Desktop to apply changes
- Test Docker connectivity: `docker context ls` and `docker version`
**Estimated Time**: 15 minutes
**Dependencies**: ENV-001

### Task 1.3: Test Docker Functionality in WSL2
**Task ID**: ENV-003
**Description**: Verify complete Docker functionality including build, run, and network operations
**Prerequisites**: ENV-002 completed, WSL2 integration enabled
**Expected Outcome**: Docker operations working correctly from WSL2 environment
**Verification Method**:
- Run hello-world container: `docker run hello-world`
- Test image pull: `docker pull nginx:alpine`
- Test container networking: `docker run -d -p 8080:80 nginx:alpine`
- Verify external access: `curl http://localhost:8080`
- Clean up test resources
**Estimated Time**: 20 minutes
**Dependencies**: ENV-002

## Phase 2: Minikube Installation and Configuration

### Task 2.1: Install Minikube Binary
**Task ID**: ENV-004
**Description**: Download and install Minikube command-line tool for Kubernetes cluster management
**Prerequisites**: ENV-003 completed, sudo access in WSL2
**Expected Outcome**: Minikube CLI installed and accessible in system PATH
**Verification Method**:
- Download latest Minikube release: `curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64`
- Install to system directory: `sudo install minikube-linux-amd64 /usr/local/bin/minikube`
- Verify installation: `minikube version`
- Test help command: `minikube --help`
**Estimated Time**: 15 minutes
**Dependencies**: ENV-003

### Task 2.2: Configure Minikube Profile
**Task ID**: ENV-005
**Description**: Create Minikube profile with optimal resource allocation for TODO Evolution development
**Prerequisites**: ENV-004 completed, sufficient system resources
**Expected Outcome**: Minikube profile configured with 4 CPUs, 8GB RAM, 20GB disk
**Verification Method**:
- Create profile: `minikube profile create todo-evolution --driver=docker`
- Configure resources: `minikube profile todo-evolution --memory=8192 --cpus=4 --disk-size=20g`
- Verify profile: `minikube profile list`
- Check profile details: `minikube profile todo-evolution`
**Estimated Time**: 20 minutes
**Dependencies**: ENV-004

### Task 2.3: Start Minikube Cluster
**Task ID**: ENV-006
**Description**: Initialize Kubernetes cluster using Docker driver with required addons
**Prerequisites**: ENV-005 completed, Docker daemon running
**Expected Outcome**: Operational Minikube cluster with ingress and monitoring addons
**Verification Method**:
- Start cluster: `minikube start --profile=todo-evolution --driver=docker`
- Enable addons: `minikube addons enable ingress metrics-server dashboard`
- Verify status: `minikube status --profile=todo-evolution`
- Test kubectl: `kubectl cluster-info`
- Check nodes: `kubectl get nodes`
**Estimated Time**: 25 minutes
**Dependencies**: ENV-005

## Phase 3: Kubernetes Tools Installation

### Task 3.1: Install kubectl
**Task ID**: ENV-007
**Description**: Install and configure Kubernetes command-line tool for cluster management
**Prerequisites**: ENV-006 completed, Minikube cluster running
**Expected Outcome**: kubectl installed and connected to Minikube cluster
**Verification Method**:
- Download kubectl: `curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"`
- Install binary: `sudo install kubectl /usr/local/bin/kubectl`
- Configure context: `minikube update-context --profile=todo-evolution`
- Verify connection: `kubectl version --client && kubectl config current-context`
**Estimated Time**: 15 minutes
**Dependencies**: ENV-006

### Task 3.2: Install Helm CLI
**Task ID**: ENV-008
**Description**: Install Helm package manager for Kubernetes application deployment
**Prerequisites**: ENV-007 completed, kubectl functional
**Expected Outcome**: Helm CLI installed and configured with stable repositories
**Verification Method**:
- Download Helm: `curl https://get.helm.sh/helm-v3.15.0-linux-amd64.tar.gz -o helm.tar.gz`
- Extract and install: `tar -zxvf helm.tar.gz && sudo mv linux-amd64/helm /usr/local/bin/helm`
- Verify installation: `helm version`
- Add repository: `helm repo add stable https://charts.helm.sh/stable && helm repo update`
**Estimated Time**: 15 minutes
**Dependencies**: ENV-007

### Task 3.3: Validate Kubernetes Tools Integration
**Task ID**: ENV-009
**Description**: Verify all Kubernetes tools are properly integrated and functional
**Prerequisites**: ENV-008 completed, kubectl and Helm installed
**Expected Outcome**: Complete Kubernetes tooling functionality confirmed
**Verification Method**:
- Test kubectl: `kubectl get nodes && kubectl get pods -A`
- Test Helm: `helm search repo nginx`
- Test Minikube integration: `minikube dashboard --url`
- Verify context: `kubectl config view`
- Test basic deployment: `kubectl create deployment test --image=nginx && kubectl delete deployment test`
**Estimated Time**: 15 minutes
**Dependencies**: ENV-008

## Phase 4: Environment Validation and Testing

### Task 4.1: Docker-Minikube Integration Test
**Task ID**: ENV-010
**Description**: Verify Docker images are accessible to Minikube and deployable
**Prerequisites**: ENV-009 completed, all tools functional
**Expected Outcome**: Docker images successfully load into Minikube and run as pods
**Verification Method**:
- Pull test image: `docker pull nginx:alpine`
- Load into Minikube: `minikube image load nginx:alpine`
- Deploy test: `kubectl create deployment test-nginx --image=nginx:alpine`
- Expose service: `kubectl expose deployment test-nginx --port=80 --type=NodePort`
- Test access: `minikube service test-nginx --url`
- Cleanup: `kubectl delete deployment test-nginx && kubectl delete service test-nginx`
**Estimated Time**: 20 minutes
**Dependencies**: ENV-009

### Task 4.2: Build TODO Evolution Containers
**Task ID**: ENV-011
**Description**: Build all TODO Evolution application container images
**Prerequisites**: ENV-010 completed, Docker-Minikube integration working
**Expected Outcome**: All three application containers built successfully
**Verification Method**:
- Build frontend: `cd frontend && docker build -t todo-frontend:1.0.0 .`
- Build backend: `cd backend && docker build -t todo-backend:1.0.0 .`
- Build MCP server: `cd mcp_server && docker build -t todo-mcp:1.0.0 .`
- Verify images: `docker images | grep todo`
- Load into Minikube: `minikube image load todo-frontend:1.0.0 todo-backend:1.0.0 todo-mcp:1.0.0`
**Estimated Time**: 20 minutes
**Dependencies**: ENV-010

### Task 4.3: Deploy TODO Evolution Test Application
**Task ID**: ENV-012
**Description**: Deploy TODO Evolution application to Minikube and verify basic functionality
**Prerequisites**: ENV-011 completed, application images built
**Expected Outcome**: TODO Evolution application successfully deployed and accessible
**Verification Method**:
- Create secrets: `kubectl create secret generic todo-secrets --from-literal=DATABASE_URL="test" --from-literal=JWT_SECRET="test" --from-literal=OPENAI_API_KEY="test"`
- Deploy application: `helm install todo-test ./todo-evolution-chart --set global.imagePullPolicy=Never`
- Monitor deployment: `kubectl get pods --watch`
- Verify services: `kubectl get services`
- Test accessibility: `minikube service todo-evolution-frontend --url`
- Cleanup: `helm uninstall todo-test && kubectl delete secret todo-secrets`
**Estimated Time**: 20 minutes
**Dependencies**: ENV-011

## Task Dependencies and Execution Order

### Sequential Dependencies
```
ENV-001 → ENV-002 → ENV-003 → ENV-004 → ENV-005 → ENV-006 → ENV-007 → ENV-008 → ENV-009 → ENV-010 → ENV-011 → ENV-012
```

### Parallel Execution Opportunities
- None: All tasks have strict sequential dependencies
- Each task must complete successfully before proceeding to the next

### Critical Path Analysis
- **Critical Path**: All 12 tasks (no parallelization possible)
- **Total Estimated Duration**: 240 minutes (4 hours)
- **Buffer Time**: 60 minutes recommended for troubleshooting

## Task Acceptance Criteria

### Phase 1 Acceptance
- Docker Desktop WSL2 integration enabled and functional
- Docker daemon accessible from WSL2 Ubuntu
- Basic Docker operations (build, run, network) working correctly

### Phase 2 Acceptance
- Minikube binary installed and accessible
- Minikube profile configured with proper resource allocation
- Kubernetes cluster operational with required addons

### Phase 3 Acceptance
- kubectl installed and connected to Minikube cluster
- Helm CLI installed with repositories configured
- All Kubernetes tools integrated and functional

### Phase 4 Acceptance
- Docker images accessible to Minikube cluster
- TODO Evolution containers built successfully
- Application deployable and accessible in Minikube

## Risk Mitigation Strategies

### High-Risk Tasks
- **ENV-002**: Docker Desktop WSL2 integration
  - **Mitigation**: Follow official documentation, restart services as needed
  - **Fallback**: Use Docker-in-Docker approach if WSL2 integration fails

- **ENV-006**: Minikube cluster startup
  - **Mitigation**: Verify Docker daemon status, check resource allocation
  - **Fallback**: Try alternative drivers (virtualbox, hyper-v) if Docker driver fails

### Medium-Risk Tasks
- **ENV-011**: Container builds
  - **Mitigation**: Check Dockerfile syntax, verify build context
  - **Fallback**: Use pre-built images if local builds fail

## Troubleshooting Commands

### Docker Issues
```bash
# Check Docker status
docker info
docker version
docker context ls

# Restart Docker Desktop
# Use Windows Services or Docker Desktop interface
```

### Minikube Issues
```bash
# Check Minikube status
minikube status --profile=todo-evolution
minikube logs --profile=todo-evolution

# Restart Minikube
minikube stop --profile=todo-evolution
minikube start --profile=todo-evolution

# Delete and recreate
minikube delete --profile=todo-evolution
minikube profile delete todo-evolution
```

### Kubernetes Issues
```bash
# Check cluster connectivity
kubectl cluster-info
kubectl get nodes
kubectl get events --sort-by=.metadata.creationTimestamp

# Reset kubectl configuration
kubectl config delete-context todo-evolution
minikube update-context --profile=todo-evolution
```

## Success Metrics

### Technical Metrics
- Docker daemon startup time: < 30 seconds
- Minikube cluster startup time: < 5 minutes
- Container build time: < 2 minutes per service
- kubectl command response time: < 2 seconds

### Functional Metrics
- 100% task completion rate
- Zero critical errors during setup
- All validation tests passing
- TODO Evolution application deployable

### Performance Metrics
- Minikube resource allocation: 4 CPUs, 8GB RAM, 20GB disk
- Container image size: Each service < 500MB
- Cluster ready time: < 10 minutes from start

## Post-Setup Validation Checklist

### Environment Validation
- [ ] Docker daemon running in WSL2
- [ ] Minikube cluster operational
- [ ] kubectl connected to cluster
- [ ] Helm CLI functional
- [ ] All tools integrated properly

### Application Validation
- [ ] TODO Evolution containers built
- [ ] Images loaded into Minikube
- [ ] Application deployable via Helm
- [ ] Services accessible via Minikube
- [ ] Health endpoints responding

### Documentation Validation
- [ ] All configuration steps documented
- [ ] Troubleshooting guide created
- [ ] Environment reset procedures available
- [ ] Team enablement materials prepared

## Completion Criteria

### Environment Ready
When all 12 tasks are completed successfully and:
- Docker Desktop WSL2 integration is functional
- Minikube cluster is running with proper resources
- All Kubernetes tools are installed and working
- TODO Evolution application can be built and deployed

### Phase D Ready
When the environment setup is complete and:
- Development team can use the environment for Kubernetes development
- TODO Evolution application can be deployed using the created Helm chart
- All validation tests are passing
- Documentation is complete and accessible

This task list provides a structured approach to environment setup with clear acceptance criteria, risk mitigation, and validation procedures.