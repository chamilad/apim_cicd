import json
import os

# env var: WSO2_APIM_ENV1_ID
env1_identifier = os.getenv("WSO2_APIM_ENV1_ID", None)
# env var: WSO2_APIM_ENV2_ID
env2_identifier = os.getenv("WSO2_APIM_ENV2_ID", None)


def propagate_filter_from_env1(unfiltered_apis):
    """
    Filter out APIs to be processed for propagation
    :param unfiltered_apis:
    :return: filtered apis
    """

    return unfiltered_apis


def propagate_change_apidef(api_definition):
    """
    Do changes to an API definition before it is applied to the next environment
    :param api_definition:
    :return: the modified api definition
    """

    # Any changes to the api definition that should be there in the new environment should be done here
    # before the create/update call is done. Refer the following examples.
    if env1_identifier is None:
        print "[ERROR] ENV1 Identifier is empty. Please set environment variable WSO2_APIM_ENV1_ID"
        exit(2)

    if env2_identifier is None:
        print "[ERROR] ENV2 Identifier is empty. Please set environment variable WSO2_APIM_ENV2_ID"
        exit(2)

    # Example 1: Replace the backend URL from dev1 to dev2
    ep_config = json.loads(api_definition["endpointConfig"])
    ep_config["production_endpoints"]["url"] = ep_config["production_endpoints"]["url"].replace(env1_identifier,
                                                                                                env2_identifier)
    ep_config["sandbox_endpoints"]["url"] = ep_config["sandbox_endpoints"]["url"].replace(env1_identifier,
                                                                                          env2_identifier)
    api_definition["endpointConfig"] = json.dumps(ep_config)

    # Example 2: Rename the API context to suite environment name
    api_definition["context"] = api_definition["context"].replace(env1_identifier, env2_identifier)

    # Example 3: Rename the API name to suite environment name
    api_definition["name"] = api_definition["name"].replace(env1_identifier, env2_identifier)

    return api_definition
