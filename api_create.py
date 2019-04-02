import glob
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
#  URLs and credentials of the API Manager deployment
# env var: WSO2_APIM_APIMGT_URL
apimgt_url = os.getenv("WSO2_APIM_APIMGT_URL", None)
# env var: WSO2_APIM_GW_URL
gw_url = os.getenv("WSO2_APIM_GW_URL", None)
# env var: WSO2_APIM_APIMGT_USERNAME
apimgt_username = os.getenv("WSO2_APIM_APIMGT_USERNAME", None)
# env var: WSO2_APIM_APIMGT_PASSWD
apimgt_pwd = os.getenv("WSO2_APIM_APIMGT_PASSWD", None)

# ignore (or not) TLS errors
# env var: WSO2_APIM_VERIFY_SSL
verify_ssl = os.getenv("WSO2_APIM_VERIFY_SSL") in ["True", "true", "yes", "1"]

# backend URLs to use when creating APIs
# env var: WSO2_APIM_BE_PROD
backend_url_prod = os.getenv("WSO2_APIM_BE_PROD", None)
# env var: WSO2_APIM_BE_SNDBX
backend_url_sandbox = os.getenv("WSO2_APIM_BE_SNDBX", None)

# The status at which the api should be created. Can be values from
# https://docs.wso2.com/display/AM260/Key+Concepts#KeyConcepts-APIlifecycle
# env var: WSO2_APIM_API_STATUS
api_status = os.getenv("WSO2_APIM_API_STATUS", "CREATED")

# Owner to be specified in the DCR
api_owner = os.getenv("WSO2_APIM_APIMGT_OWNER", None)

#
# 2. Sanitize input
#
# Any empty or invalid value should result in an immediate exit.
#
if apimgt_url is None:
    print "[ERROR] API Manager URL is empty. Please set environment variable WSO2_APIM_APIMGT_URL"
    exit(2)

if gw_url is None:
    print "[ERROR] Gateway URL is empty. Please set environment variable WSO2_APIM_GW_URL"
    exit(2)

if apimgt_username is None:
    print "[ERROR] API Manager Username is empty. Please set environment variable WSO2_APIM_APIMGT_USERNAME"
    exit(2)

if apimgt_pwd is None:
    print "[ERROR] API Manager Password is empty. Please set environment variable WSO2_APIM_APIMGT_PASSWD"
    exit(2)

if verify_ssl is None:
    print "[ERROR] Verify_SSL flag is empty. Please set environment variable WSO2_APIM_VERIFY_SSL"
    exit(2)

if backend_url_prod is None:
    print "[ERROR] Production Backend URL is empty. Please set environment variable WSO2_APIM_BE_PROD"
    exit(2)

if backend_url_sandbox is None:
    print "[ERROR] Sandbox Backend URL is empty. Please set environment variable WSO2_APIM_BE_SNDBX"
    exit(2)

if api_status is None:
    print "[ERROR] API Status is empty. Please set environment variable WSO2_APIM_API_STATUS"
    exit(2)

if api_status not in ["CREATED", "PROTOTYPED", "PUBLISHED", "BLOCKED", "DEPRECATED", "RETIRED"]:
    print "[ERROR] API Status is an invalid value. Please set environment variable WSO2_APIM_API_STATUS with values " \
          "found in https://docs.wso2.com/display/AM260/Key+Concepts#KeyConcepts-APIlifecycle"
    exit(2)

if api_owner is None:
    print "[ERROR] API Owner is empty. Please set environment variable WSO2_APIM_APIMGT_OWNER"
    exit(2)

# Run the following for the Python script execution
if __name__ == '__main__':
    print "Obtaining access token..."
    access_token = api_utils.get_access_token(apimgt_url, gw_url, apimgt_username, apimgt_pwd, api_owner, verify_ssl)

    if access_token is None:
        print "[ERROR] Error when obtaining access token. Aborting..."
        exit(1)

    # Iterate through all json files inside api_definitions
    api_requests = {}

    for api_request_file in glob.glob("api_definitions/*_apis.json"):
        request_json_content = json.loads(open(api_request_file).read())
        requesting_user = request_json_content["username"]
        department = request_json_content["department"]

        print "Parsing create requests for [user] %s [department] %s [requests] %s..." % (
            requesting_user, department, len(request_json_content["apis"]))

        # For each api request, it should be checked whether an API with the same name already exists.
        # If an API with the same name exists, it should be checked if there is an existing version matching the
        # version requested.
        #
        # If there is no matching API, an API create request is done.
        # If a matching API is there, but no matching version, a version would be added
        # If both a matching API with a matching version exists, the API would not be created.
        for api_request in request_json_content["apis"]:
            api_name_exists, api_id = api_utils.api_name_exists(api_request["name"], apimgt_url, access_token,
                                                                verify_ssl)

            if api_name_exists:
                # Check if the same version exists
                api_version_exists, _ = api_utils.api_version_exists(api_request["name"], api_request["version"],
                                                                     apimgt_url, access_token, verify_ssl)
                if api_version_exists:
                    # Do not create the same version
                    print "\t%s:%s \t :Exists. Skipping..." % (api_request["name"], api_request["version"])
                    continue
                else:
                    # Add as a new version
                    print "\t%s:%s \t :Adding version..." % (api_request["name"], api_request["version"])
                    addVersionSuccessful, apiId = api_utils.add_api_version(api_id, api_request["version"], apimgt_url, access_token, verify_ssl)

                    if not addVersionSuccessful:
                        print "[ERROR] API new version addition failed. [server] %s. Continuing..." % apimgt_url

                    # Get apiId from create response and then publish
                    publishSuccessful = api_utils.change_lifecycle(apiId, "Publish", apimgt_url, access_token, verify_ssl)

                    if not publishSuccessful:
                        print "[ERROR] API publish failed. [server] %s. Continuing..." % apimgt_url
            else:
                # Create API
                print "\t%s:%s \t :Creating..." % (api_request["name"], api_request["version"])

                # Build API Create request
                create_req_body = json.loads(open("api_template.json").read())
                create_req_body["name"] = api_request["name"]
                create_req_body["description"] = api_request["description"]
                create_req_body["context"] = api_request["context"]
                create_req_body["version"] = api_request["version"]
                create_req_body["provider"] = requesting_user
                create_req_body["tags"].append(department)
                create_req_body["businessInformation"]["businessOwnerEmail"] = requesting_user
                create_req_body["businessInformation"]["technicalOwnerEmail"] = requesting_user
                create_req_body["businessInformation"]["businessOwner"] = requesting_user
                create_req_body["businessInformation"]["technicalOwner"] = requesting_user
                create_req_body["status"] = api_status
                create_req_body["accessControl"] = "RESTRICTED"
                # API creation will fail if role does not exist in userstore
                create_req_body["accessControlRoles"].append(department)
                create_req_body["visibleRoles"].append(department)

                ep_config = json.loads(create_req_body["endpointConfig"])
                ep_config["production_endpoints"]["url"] = backend_url_prod
                ep_config["sandbox_endpoints"]["url"] = backend_url_sandbox

                create_req_body["endpointConfig"] = json.dumps(ep_config)

                if "apiDefinition" in api_request:
                    create_req_body["apiDefinition"] = api_request["apiDefinition"]
                else:
                    swagger_def = json.loads(create_req_body["apiDefinition"])
                    swagger_def["info"]["title"] = api_request["name"]
                    swagger_def["info"]["description"] = api_request["description"]
                    swagger_def["info"]["version"] = api_request["version"]
                    swagger_def["info"]["contact"]["email"] = requesting_user
                    swagger_def["info"]["contact"]["name"] = requesting_user

                    create_req_body["apiDefinition"] = json.dumps(swagger_def)

                successful, apiId = api_utils.create_api(create_req_body, apimgt_url, access_token, verify_ssl)

                if not successful:
                    print "[ERROR] API creation failed. [server] %s. Continuing..." % apimgt_url

                # Get apiId from create response and then publish
                publishSuccessful = api_utils.change_lifecycle(apiId, "Publish", apimgt_url, access_token, verify_ssl)

                if not publishSuccessful:
                    print "[ERROR] API publish failed. [server] %s. Continuing..." % apimgt_url

    print
    print "DONE!"
    exit(0)
