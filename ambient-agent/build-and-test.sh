#!/bin/bash
# Build and test script for Ambient Agent

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="ambient-agent"
IMAGE_TAG="latest"
REGISTRY="quay.io/YOUR_ORG"  # Update this!
FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Ambient Agent Build & Test${NC}"
echo -e "${GREEN}========================================${NC}"

# Step 1: Build the container
echo -e "\n${YELLOW}Step 1: Building container image...${NC}"
podman build -t ${IMAGE_NAME}:${IMAGE_TAG} -f Containerfile .

if [ $? -eq 0 ]; then
    echo -e "${GREEN} Build successful!${NC}"
else
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

# Step 2: Test locally
echo -e "\n${YELLOW}Step 2: Testing container locally...${NC}"
echo "Starting container (will run for 30 seconds)..."

# Run container in background
CONTAINER_ID=$(podman run -d \
    --name ambient-agent-test \
    ${IMAGE_NAME}:${IMAGE_TAG})

echo "Container ID: ${CONTAINER_ID}"

# Wait a bit for startup
sleep 5

# Check if container is running
if podman ps | grep -q ambient-agent-test; then
    echo -e "${GREEN} Container is running${NC}"
    
    # Show logs
    echo -e "\n${YELLOW}Container logs:${NC}"
    podman logs ambient-agent-test
    
    # Let it run for a bit
    echo -e "\nLetting container run for 25 more seconds..."
    sleep 25
    
    # Final logs
    echo -e "\n${YELLOW}Final logs:${NC}"
    podman logs --tail 20 ambient-agent-test
else
    echo -e "${RED}❌ Container failed to start${NC}"
    podman logs ambient-agent-test
    podman rm -f ambient-agent-test 2>/dev/null || true
    exit 1
fi

# Cleanup
echo -e "\n${YELLOW}Cleaning up test container...${NC}"
podman stop ambient-agent-test
podman rm ambient-agent-test

echo -e "${GREEN} Local test complete!${NC}"

# Step 3: Push to registry (optional)
echo -e "\n${YELLOW}Step 3: Push to registry?${NC}"
read -p "Do you want to push to ${FULL_IMAGE}? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Tagging image..."
    podman tag ${IMAGE_NAME}:${IMAGE_TAG} ${FULL_IMAGE}
    
    echo "Pushing to registry..."
    podman push ${FULL_IMAGE}
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN} Push successful!${NC}"
        echo -e "\nUpdate openshift/02-deployment.yaml with:"
        echo -e "  image: ${FULL_IMAGE}"
    else
        echo -e "${RED}❌ Push failed!${NC}"
        exit 1
    fi
else
    echo "Skipping push."
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Build & Test Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\nNext steps:"
echo -e "1. Update openshift/02-deployment.yaml with your image"
echo -e "2. Apply to OpenShift:"
echo -e "   oc apply -f openshift/01-configmap.yaml"
echo -e "   oc apply -f openshift/02-deployment.yaml"
echo -e "3. Check logs:"
echo -e "   oc logs -f deployment/ambient-agent"

