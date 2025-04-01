#!/bin/bash

# Ensure secrets directory exists
mkdir -p secrets

# Check if secrets already exist
if [ -f secrets/webserver_secret_key ] && 
   [ -f secrets/postgres_password ] && 
   [ -f secrets/airflow_admin_password ]; then
    echo "Secrets already exist. Skipping generation."
    exit 0
fi

# Generate Secret Key for Webserver
echo "Generating Webserver Secret Key..."
python3 -c 'import secrets; print(secrets.token_hex(32))' > secrets/webserver_secret_key

# Generate Postgres Password
echo "Generating Postgres Password..."
python3 -c 'import secrets; print(secrets.token_urlsafe(16))' > secrets/postgres_password

# Generate Airflow Admin Password
echo "Generating Airflow Admin Password..."
python3 -c 'import secrets; print(secrets.token_urlsafe(12))' > secrets/airflow_admin_password

# Set Secure Permissions
chmod 600 secrets/*

echo "Secrets generated successfully in the 'secrets' directory."
