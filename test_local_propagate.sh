#!/usr/bin/env bash

if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Setting virtual environment..."
    source venv/bin/activate
fi

echo "Setting environment variables to point to the localhost..."
export WSO2_APIM_ENV1_APIMGT_URL="https://172.17.0.1:9443"
export WSO2_APIM_ENV1_GW_URL="https://172.17.0.1:8243"
export WSO2_APIM_ENV1_APIMGT_USERNAME="admin"
export WSO2_APIM_ENV1_APIMGT_PASSWD="admin"
# WSO2_APIM_ENV1_ID should be lowercase
export WSO2_APIM_ENV1_ID="dev1"
export WSO2_APIM_ENV1_APIMGT_OWNER="admin"

export WSO2_APIM_ENV2_APIMGT_URL="https://172.17.0.1:9543"
export WSO2_APIM_ENV2_GW_URL="https://172.17.0.1:8343"
export WSO2_APIM_ENV2_APIMGT_USERNAME="admin"
export WSO2_APIM_ENV2_APIMGT_PASSWD="admin"
# WSO2_APIM_ENV2_ID should be lowercase
export WSO2_APIM_ENV2_ID="dev11"
export WSO2_APIM_ENV2_APIMGT_OWNER="admin"

# WSO2_APIM_API_PREFIX should be lowercase
export WSO2_APIM_API_PREFIX="cjams"

export WSO2_APIM_VERIFY_SSL="False"

export WSO2_APIM_VERBOSE="False"

echo "Running Python script..."
python2 api_propagate.py
