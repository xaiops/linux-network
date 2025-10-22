# Ambient Agent - OpenShift Deployment Guide

## 📋 Prerequisites

- Podman installed
- Access to OpenShift cluster (`oc` CLI configured)
- Container registry access (Quay.io or internal registry)

---

## 🚀 Quick Start

### Step 1: Build Container

```bash
cd /Users/raghurambanda/playground/linux-network/ambient-agent

# Run build script
./build-and-test.sh
```

This will:
1. Build container image with Podman
2. Test it locally for 30 seconds
3. Ask if you want to push to registry

### Step 2: Update Configuration

Edit `openshift/02-deployment.yaml`:
```yaml
spec:
  containers:
  - name: agent
    image: quay.io/YOUR_ORG/ambient-agent:latest  # ← Update this!
```

### Step 3: Deploy to OpenShift

```bash
# Create namespace (if needed)
oc new-project ambient-monitoring

# Deploy
oc apply -f openshift/01-configmap.yaml
oc apply -f openshift/02-deployment.yaml

# Check status
oc get pods
oc logs -f deployment/ambient-agent
```

---

## 🧪 Manual Testing

### Test Locally with Podman

```bash
# Build
podman build -t ambient-agent:latest -f Containerfile .

# Run (will monitor every 5 minutes)
podman run --rm ambient-agent:latest

# Run with custom config
podman run --rm \
  -v $(pwd)/config.yaml:/opt/app-root/src/ambient-agent/config.yaml:Z \
  ambient-agent:latest
```

### Test on OpenShift

```bash
# Watch logs live
oc logs -f deployment/ambient-agent

# Check for errors
oc describe pod -l app=ambient-agent

# Restart if needed
oc rollout restart deployment/ambient-agent

# Scale down/up
oc scale deployment/ambient-agent --replicas=0
oc scale deployment/ambient-agent --replicas=1
```

---

## 📁 File Structure

```
ambient-agent/
├── Containerfile                # Container build definition
├── requirements.txt             # Python dependencies
├── .containerignore            # Exclude files from build
├── build-and-test.sh           # Build & test script
├── src/                        # Application code
├── config.yaml                 # Local config (template)
└── openshift/
    ├── 01-configmap.yaml       # OpenShift config
    └── 02-deployment.yaml      # OpenShift deployment
```

---

## ⚙️ Configuration

### Update ConfigMap

Edit `openshift/01-configmap.yaml` to change:
- MCP server endpoint
- Target RHEL server
- LLM settings
- Alert configuration
- Monitoring interval

Then apply:
```bash
oc apply -f openshift/01-configmap.yaml
oc rollout restart deployment/ambient-agent  # Restart to pickup changes
```

---

## 🔍 Troubleshooting

### Container won't start

```bash
# Check logs
oc logs deployment/ambient-agent

# Check events
oc get events --sort-by='.lastTimestamp'

# Describe pod
oc describe pod -l app=ambient-agent
```

### Can't reach MCP server

```bash
# Test connectivity from pod
oc exec deployment/ambient-agent -- curl -v http://linux-mcp-server:8000/mcp

# Check if MCP service exists
oc get svc linux-mcp-server
```

### Out of memory

Increase resources in `02-deployment.yaml`:
```yaml
resources:
  limits:
    memory: "1Gi"  # Increase from 512Mi
```

### Logs not appearing

Check the log path in config:
```yaml
alerts:
  log_file: "/opt/app-root/src/ambient-agent/logs/alerts.log"
```

View logs:
```bash
oc exec deployment/ambient-agent -- cat /opt/app-root/src/ambient-agent/logs/alerts.log
```

---

## 📊 Monitoring

### View Agent Activity

```bash
# Follow logs
oc logs -f deployment/ambient-agent

# Get last 100 lines
oc logs --tail=100 deployment/ambient-agent

# Logs from previous crash
oc logs --previous deployment/ambient-agent
```

### Check Resource Usage

```bash
# CPU and memory
oc adm top pod -l app=ambient-agent

# Detailed metrics
oc describe pod -l app=ambient-agent | grep -A 5 "Limits:"
```

---

## 🔄 Updates

### Deploy New Version

```bash
# Build new image
./build-and-test.sh

# Update image in deployment (if using different tag)
oc set image deployment/ambient-agent agent=quay.io/YOUR_ORG/ambient-agent:v2

# Or just restart (if using :latest)
oc rollout restart deployment/ambient-agent

# Watch rollout
oc rollout status deployment/ambient-agent
```

---

## 🗑️ Cleanup

```bash
# Delete deployment
oc delete -f openshift/02-deployment.yaml
oc delete -f openshift/01-configmap.yaml

# Or delete entire project
oc delete project ambient-monitoring
```

---

## 📝 Notes

- **No persistent storage** - Logs are in `emptyDir` (lost on restart)
- **For production** - Add PersistentVolumeClaim for logs
- **Monitoring interval** - Default 5 minutes (configurable)
- **Replicas** - Should be 1 (don't scale horizontally)
- **Restarts** - Deployment will auto-restart on failure

---

##  Success Checklist

- [ ] Container builds successfully
- [ ] Local podman test passes
- [ ] Image pushed to registry
- [ ] ConfigMap deployed
- [ ] Deployment created
- [ ] Pod is running
- [ ] Logs show monitoring cycles
- [ ] Can reach MCP server
- [ ] Alerts being written

---

Ready to deploy! 🚀

