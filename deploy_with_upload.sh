#!/bin/bash
cdk deploy "$@"
if [ $? -eq 0 ]; then
    echo "CDK Deploy succeeded. Running post-deploy script..."
    python upload_dictionaries.py
else
    echo "CDK Deploy failed. Skipping post-deploy script."
fi
