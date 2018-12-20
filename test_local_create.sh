#!/usr/bin/env bash

if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Setting virtual environment..."
    source venv/bin/activate
fi

echo "Setting environment variables to point to the localhost..."
export WSO2_APIM_APIMGT_URL="https://172.17.0.1:9443"
export WSO2_APIM_GW_URL="https://172.17.0.1:8243"
export WSO2_APIM_APIMGT_USERNAME="admin"
export WSO2_APIM_APIMGT_PASSWD="admin"

export WSO2_APIM_VERIFY_SSL="False"

export WSO2_APIM_BE_PROD="http://mybackendserver.dev1.client.test/apibase"
export WSO2_APIM_BE_SNDBX="http://mybackendserver.dev1.client.test/apibase"

export WSO2_APIM_API_STATUS="CREATED"

export WSO2_APIM_VERBOSE="False"

echo "Running Python script..."
python2 api_create.py
