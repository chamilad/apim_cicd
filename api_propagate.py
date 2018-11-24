import json
import os

import api_utils

#
# Exit codes
# ============
# 0 - Exit without issue
# 1 - Connection issue
# 2 - An input is not of the expected value

#
# Start execution
#
# 1. Load values from environment variables
#
# URLs and credentials of the API Manager deployment ENV1
# env var: WSO2_APIM_ENV1_APIMGT_URL
env1_apimgt_url = os.getenv("WSO2_APIM_ENV1_APIMGT_URL", None)
# env var: WSO2_APIM_ENV1_GW_URL
env1_gw_url = os.getenv("WSO2_APIM_ENV1_GW_URL", None)
# env var: WSO2_APIM_ENV1_APIMGT_USERNAME
env1_apimgt_username = os.getenv("WSO2_APIM_ENV1_APIMGT_USERNAME", None)
# env var: WSO2_APIM_ENV1_APIMGT_PASSWD
env1_apimgt_pwd = os.getenv("WSO2_APIM_ENV1_APIMGT_PASSWD", None)

# URLs and credentials of the API Manager deployment ENV2
# env var: WSO2_APIM_ENV2_APIMGT_URL
env2_apimgt_url = os.getenv("WSO2_APIM_ENV2_APIMGT_URL", None)
# env var: WSO2_APIM_ENV2_GW_URL
env2_gw_url = os.getenv("WSO2_APIM_ENV2_GW_URL", None)
# env var: WSO2_APIM_ENV2_APIMGT_USERNAME
env2_apimgt_username = os.getenv("WSO2_APIM_ENV2_APIMGT_USERNAME", None)
# env var: WSO2_APIM_ENV2_APIMGT_PASSWD
env2_apimgt_pwd = os.getenv("WSO2_APIM_ENV2_APIMGT_PASSWD", None)

# ignore TLS errors
# env var: WSO2_APIM_VERIFY_SSL
verify_ssl = os.getenv("WSO2_APIM_VERIFY_SSL") in ["True", "true", "yes", "1"]

#
# 2. Sanitize input
#
# Any empty or invalid value should result in an immediate exit.
#
if env1_apimgt_url is None:
    print "[ERROR] ENV1 API Manager URL is empty. Please set environment variable WSO2_APIM_ENV1_APIMGT_URL"
    exit(2)

if env1_gw_url is None:
    print "[ERROR] ENV1 Gateway URL is empty. Please set environment variable WSO2_APIM_ENV1_GW_URL"
    exit(2)

if env1_apimgt_username is None:
    print "[ERROR] ENV1 API Manager Username is empty. Please set environment variable WSO2_APIM_ENV1_APIMGT_USERNAME"
    exit(2)

if env1_apimgt_pwd is None:
    print "[ERROR] ENV1 API Manager Password is empty. Please set environment variable WSO2_APIM_ENV1_APIMGT_PASSWD"
    exit(2)

if env2_apimgt_url is None:
    print "[ERROR] ENV2 API Manager URL is empty. Please set environment variable WSO2_APIM_ENV2_APIMGT_URL"
    exit(2)

if env2_gw_url is None:
    print "[ERROR] ENV2 Gateway URL is empty. Please set environment variable WSO2_APIM_ENV2_GW_URL"
    exit(2)

if env2_apimgt_username is None:
    print "[ERROR] ENV2 API Manager Username is empty. Please set environment variable WSO2_APIM_ENV2_APIMGT_USERNAME"
    exit(2)

if env2_apimgt_pwd is None:
    print "[ERROR] ENV2 API Manager Password is empty. Please set environment variable WSO2_APIM_ENV2_APIMGT_PASSWD"
    exit(2)

if verify_ssl is None:
    print "[ERROR] Verify_SSL flag is empty. Please set environment variable WSO2_APIM_VERIFY_SSL"
    exit(2)

# Main script execution
if __name__ == '__main__':
    print "Obtaining access token for ENV1..."
    env1_access_token = api_utils.get_access_token(env1_apimgt_url, env1_gw_url, env1_apimgt_username, env1_apimgt_pwd,
                                                   verify_ssl)
    if env1_access_token is None:
        print "[ERROR] Error when obtaining access token from ENV1. Aborting..."
        exit(1)

    # 1. Get list of APIs from env1
    print "Getting the list of APIs from ENV1..."
    all_apis_in_env1 = api_utils.get_all_apis(env1_apimgt_url, env1_access_token, verify_ssl)

    if all_apis_in_env1 is None:
        print "Error while retrieving API details from env1. Aborting..."
        exit(1)

    if all_apis_in_env1["count"] == 0:
        print "No APIs were found in env1. Exiting..."
        exit(0)

    # 2. Iterate through APIs and check if exists in env2
    print "Obtaining access token for ENV2..."
    env2_access_token = api_utils.get_access_token(env2_apimgt_url, env2_gw_url, env2_apimgt_username, env2_apimgt_pwd,
                                                   verify_ssl)
    if env2_access_token is None:
        print "[ERROR] Error when obtaining access token from ENV2. Aborting..."
        exit(1)

    print "Checking for API status in ENV2..."
    for api_to_propagate in all_apis_in_env1["list"]:
        # get the api definition from env 1
        api_definition_env1 = api_utils.get_api_by_id(api_to_propagate["id"], env1_apimgt_url, env1_access_token,
                                                      verify_ssl)

        if api_definition_env1 is None:
            print "Couldn't retrieve API info [api-id] %s [api-name] %s. Continuing..." % (
                api_to_propagate["id"], api_to_propagate["name"])
            continue

        # delete the API ID from the create request
        del api_definition_env1["id"]

        # Any changes to the api definition that should be there in the new environment should be done here
        # before the create/update call is done. Refer the following examples.

        # Example 1: Replace the backend URL from dev1 to dev2
        ep_config = json.loads(api_definition_env1["endpointConfig"])
        ep_config["production_endpoints"]["url"] = ep_config["production_endpoints"]["url"].replace("dev1", "dev2")
        ep_config["sandbox_endpoints"]["url"] = ep_config["sandbox_endpoints"]["url"].replace("dev1", "dev2")
        api_definition_env1["endpointConfig"] = json.dumps(ep_config)

        # Example 2: Rename the API context to suite environment name
        api_definition_env1["context"] = api_definition_env1["context"].replace("dev1", "dev2")

        # Example 3: Rename the API name to suite environment name
        api_definition_env1["name"] = api_definition_env1["name"].replace("dev1", "dev2")

        # check if API exists in env2
        api_exists_in_env2, api_id = api_utils.api_version_exists(api_definition_env1["name"], api_definition_env1["version"],
                                                                  env2_apimgt_url, env2_access_token, verify_ssl)

        if api_exists_in_env2:
            # 3. If exists, update API

            # check the kind of api_id received.. should be a UUID
            if "-" not in api_id:
                print "Abnormal state found where more than one (%s) api-version was found for [api-name] %s " \
                      "[api-version] %s. Skipping this one..." % (
                          api_id, api_definition_env1["name"], api_definition_env1["version"])

                continue

            api_definition_env1["id"] = api_id

            print "Updating API %s in ENV2..." % api_definition_env1["name"]
            api_utils.update_api(api_definition_env1, env2_apimgt_url, env2_access_token, verify_ssl)
        else:
            # 4 If doesn't exist, create API in env2

            # Delete apiSecurity element in the GET api response before creating API
            if "apiSecurity" in api_definition_env1:
                del api_definition_env1["apiSecurity"]

            print "Creating API %s in ENV2..." % api_definition_env1["name"]
            api_utils.create_api(api_definition_env1, env2_apimgt_url, env2_access_token, verify_ssl)

    print
    print "DONE!"
    exit(0)
