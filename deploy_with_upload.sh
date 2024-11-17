#!/bin/bash

# Navigate to the backend directory relative to the script location
cd "$(dirname "$0")/backend"

# Run CDK deploy
cdk deploy "$@"
if [ $? -eq 0 ]; then
    echo "CDK Deploy succeeded. Running post-deploy script..."
    # Run the post-deploy dictionary upload script
    python3 upload_dictionaries.py
else
    echo "CDK Deploy failed. Skipping post-deploy script."
fi
