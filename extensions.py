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
        "query": "context:*/" + env1_identifier + "/*"
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
