import json
import os

"""
extensions.py

The purpose of this Python script is to offer extensibility to the CI/CD functions
being done by the api_create.py and api_propagate.py scripts. The extension points 
can be several points in the process. At each point, the scripts can call the methods
in the extensions.py. The changes needed can be done in this script can be done 
without interfering with the core logic and without the fear of breaking the logic. 

It should be noted that incorrect values returned by the following implementations
could actually break the core logic. Therefore, carefully study the sample 
implementations before modifying the behavior. 
"""

# env var: WSO2_APIM_API_PREFIX
api_prefix = os.getenv("WSO2_APIM_API_PREFIX", None)
# env var: WSO2_APIM_ENV1_ID
env1_identifier = os.getenv("WSO2_APIM_ENV1_ID", None)
# env var: WSO2_APIM_ENV2_ID
env2_identifier = os.getenv("WSO2_APIM_ENV2_ID", None)


def propagate_filter_api_env1_by():
    """
    Filter out APIs to be processed for propagation

    For an example, the following default implementation filters
    the APIs by the presence of /devX/ in the API context, X being
    the environment number. Any more filtering can also be done
    by modifying this method.

    :return: query filter to retrieve apis from ENV1
    """

    filter_query_params = {
        "query": "context:*/" + api_prefix + "/" + env1_identifier + "/*"
    }

    return filter_query_params


def propagate_change_apidef(api_definition):
    """
    Do changes to an API definition before it is applied to the next environment.

    The following default implementation changes the environment specific identifiers
    present in the context, endpoints, and the API name to match the target environment.

    :param api_definition:
    :return: the modified api definition
    """

    # Any changes to the api definition that should be there in the new environment should be done here
    # before the create/update call is done. Refer the following examples.
    if api_prefix is None:
        print "[ERROR] API Prefix is empty. Please set environment variable WSO2_APIM_API_PREFIX"
        exit(2)

    if env1_identifier is None:
        print "[ERROR] ENV1 Identifier is empty. Please set environment variable WSO2_APIM_ENV1_ID"
        exit(2)

    if env2_identifier is None:
        print "[ERROR] ENV2 Identifier is empty. Please set environment variable WSO2_APIM_ENV2_ID"
        exit(2)

    env1_url_replace_string = env1_identifier + "-" + api_prefix
    env2_url_replace_string = env2_identifier + "-" + api_prefix
    env1_context_replace_string = api_prefix + "/" + env1_identifier
    env2_context_replace_string = api_prefix + "/" + env2_identifier
    env1_name_replace_string = (api_prefix + "_" + env1_identifier).upper()
    env2_name_replace_string = (api_prefix + "_" + env2_identifier).upper()

    #Example: Replace the backend URL from http://dev1-cjams-app.mdcloud.local/api to http://dev2-cjams-app.mdcloud.local/api
    ep_config = json.loads(api_definition["endpointConfig"])
    ep_config["production_endpoints"]["url"] = ep_config["production_endpoints"]["url"].replace(env1_url_replace_string,
                                                                                                env2_url_replace_string)
    ep_config["sandbox_endpoints"]["url"] = ep_config["sandbox_endpoints"]["url"].replace(env1_url_replace_string,
                                                                                          env2_url_replace_string)
    api_definition["endpointConfig"] = json.dumps(ep_config)

    #Example: Rename the API context from /api/cjams/dev1/accessTkn/v1 to /api/cjams/dev2/accessTkn/v1
    api_definition["context"] = api_definition["context"].replace(env1_context_replace_string, env2_context_replace_string)

    #Example: Rename the API name from CJAMS_DEV1_ACCESSTKN_API - v1 to CJAMS_DEV2_ACCESSTKN_API - v1
    api_definition["name"] = api_definition["name"].replace(env1_name_replace_string, env2_name_replace_string)

    return api_definition
