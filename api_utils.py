import base64
import os

import requests
import urllib3

# Hide SSL verification warning for now
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Publisher API endpoints
# {x} will be replaced with values later with str.format()
dcr_ep = "{0}/client-registration/v0.14/register"
token_ep = "{0}/token"
apis_ep = "{0}/api/am/publisher/v0.14/apis{1}"
api_versions_ep = "{0}/api/am/publisher/v0.14/apis/copy-api"

# Set to true for verbose logging in http calls
verbose = os.getenv("WSO2_APIM_VERBOSE") in ["True", "true", "yes", "1"]


def do_post(url, req_body=None, req_headers=None, query_params=None, verify_ssl=True, json_body=False):
    """
    Make HTTP POST requests
    :param query_params:
    :param url:
    :param req_body:
    :param req_headers:
    :param verify_ssl:
    :param json_body: True if the request body should be sent as JSON, false if set as form data
    :return:
    """
    if query_params is None:
        query_params = {}

    if req_headers is None:
        req_headers = {}

    if req_body is None:
        req_body = {}

    try:
        if json_body:
            raw_response = requests.post(url=url, json=req_body, headers=req_headers, params=query_params,
                                         verify=verify_ssl)
        else:
            raw_response = requests.post(url=url, data=req_body, headers=req_headers, params=query_params,
                                         verify=verify_ssl)

        print_verbose_details(raw_response)

        return True, raw_response.status_code, raw_response.json()

    except requests.exceptions.Timeout as e:
        print "[ERROR] HTTP_POST: Timeout. [url] %s [verify ssl] %s" % (url, verify_ssl)
        return False, None, "Timeout: " + e.message
    except Exception as e:
        print "[ERROR] HTTP_POST: Other error. %s, [url] %s [verify ssl] %s" % (e, url, verify_ssl)
        return False, None, e.message


def print_verbose_details(raw_response):
    """
    Print details of an HTTP response object, if Verbose mode is set to True.

    :param raw_response:
    :return:
    """
    if verbose:
        print "REQ: Headers --------------------------------"
        print raw_response.request.headers
        print "REQ: Body -----------------------------------"
        print raw_response.request.body
        print "RES: Status code ----------------------------"
        print raw_response.status_code
        print "RES: Headers --------------------------------"
        print raw_response.headers
        print "RES: Body -----------------------------------"
        print raw_response.json()
        print "---------------------------------------------\n"


def do_put(url, req_body=None, req_headers=None, query_params=None, verify_ssl=True, json_body=False):
    """
    Make HTTP PUT requests
    :param query_params:
    :param url:
    :param req_body:
    :param req_headers:
    :param verify_ssl:
    :param json_body: True if the request body should be sent as JSON, false if not
    :return:
    """
    if query_params is None:
        query_params = {}

    if req_headers is None:
        req_headers = {}

    if req_body is None:
        req_body = {}

    try:
        if json_body:
            raw_response = requests.put(url=url, json=req_body, headers=req_headers, params=query_params,
                                        verify=verify_ssl)
        else:
            raw_response = requests.put(url=url, data=req_body, headers=req_headers, params=query_params,
                                        verify=verify_ssl)

        print_verbose_details(raw_response)

        return True, raw_response.status_code, raw_response.json()

    except requests.exceptions.Timeout as e:
        print "[ERROR] Timeout. [url] %s [verify ssl] %s" % (url, verify_ssl)
        return False, None, "Timeout: " + e.message
    except Exception as e:
        print "[ERROR] Other error. %s, [url] %s [verify ssl] %s" % (e, url, verify_ssl)
        return False, None, "Timeout: " + e.message


def do_get(url, req_params=None, req_headers=None, verify_ssl=True):
    """
    Make HTTP GET requests
    :param url:
    :param req_params:
    :param req_headers:
    :param verify_ssl:
    :return:
    """
    if req_params is None:
        req_params = {}

    if req_headers is None:
        req_headers = {}

    try:
        raw_response = requests.get(url, params=req_params, headers=req_headers, verify=verify_ssl)

        print_verbose_details(raw_response)

        return True, raw_response.status_code, raw_response.json()

    except requests.exceptions.Timeout as e:
        print "[ERROR] Timeout. [url] %s [verify ssl] %s" % (url, verify_ssl)
        return False, None, "Timeout: " + e.message
    except Exception as e:
        print "[ERROR] Other error. %s, [url] %s [verify ssl] %s" % (e, url, verify_ssl)
        return False, None, "Timeout: " + e.message


def get_access_token(apimgt_url, gw_url, username, password, owner, verify_ssl=True):
    """
    Do Dynamic Client registration and obtain an access token to be used for Publisher API calls
    :return:
    """
    dcr_req_body = {
        'callbackUrl': 'www.google.lk',
        'clientName': 'rest_api_publisher',
        'tokenScope': 'Production',
        'owner': owner,
        'grantType': 'password refresh_token',
        'saasApp': 'true'
    }

    # base64 encoded credentials for basic auth
    creds_b64 = base64.encodestring(username + ":" + password).strip()
    dcr_req_headers = {
        'Content-Type': 'application/json',
        "Authorization": "Basic %s" % creds_b64
    }

    # do DCR request
    successful, sc, dcr_response = do_post(dcr_ep.format(apimgt_url), dcr_req_body, dcr_req_headers,
                                           verify_ssl=verify_ssl, json_body=True)

    if not successful:
        print "[ERROR] DCR request failed. [status-code] %s [url] %s" % (sc, dcr_ep.format(apimgt_url))
        return None

    # base64 encode the received client ID and client secret
    cics_b64 = base64.encodestring(dcr_response["clientId"] + ":" + dcr_response["clientSecret"])

    token_req_body = {
        'scope': 'apim:api_view apim:api_create apim:api_publish',
        'grant_type': 'password',
        'username': username,
        'password': password
    }

    token_req_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic %s" % cics_b64.strip()
    }

    # make token request
    successful, sc, token_response = do_post(token_ep.format(gw_url), token_req_body, token_req_headers,
                                             verify_ssl=verify_ssl)

    if not successful:
        print "[ERROR] Token request failed. [status-code] %s [url] %s" % (sc, token_ep.format(gw_url))
        return None

    return token_response["access_token"]


def get_all_apis(apimgt_url, access_token, query_params=None, verify_ssl=False):
    """
    Get a list of APIs with provided query. If no query data is provided, all APIs will be returned.

    :param apimgt_url:
    :param access_token:
    :param query_params:
    :param verify_ssl:
    :return:
    """
    if query_params is None:
        query_params = {}

    get_api_req_headers = {
        "Authorization": "Bearer " + access_token.strip()
    }

    successful, sc, api_response = do_get(apis_ep.format(apimgt_url, ""), req_params=query_params,
                                          req_headers=get_api_req_headers,
                                          verify_ssl=verify_ssl)

    if successful:
        return api_response

    print "[ERROR] Get:All-APIs call failed [status-code] %s [url] %s" % (sc, apis_ep.format(apimgt_url, ""))
    return None


def get_api_by_id(api_id, apimgt_url, access_token, verify_ssl=False):
    req_headers = {
        "Authorization": "Bearer " + access_token.strip()
    }

    successful, sc, api_response = do_get(apis_ep.format(apimgt_url, "/" + api_id), req_headers=req_headers,
                                          verify_ssl=verify_ssl)

    if successful:
        return api_response

    print "[ERROR] Get:API call failed [status-code] %s [url] %s" % (sc, apis_ep.format(apimgt_url, "/" + api_id))
    return None


def api_name_exists(api_name, apimgt_url, access_token, verify_ssl=False):
    """
    Check if the given API exists by name
    :param api_name:
    :param apimgt_url:
    :param access_token:
    :param verify_ssl:
    :return:
    """
    get_api_req_params = {
        "query": "name:" + api_name
    }

    api_search_response = get_all_apis(apimgt_url, access_token, query_params=get_api_req_params, verify_ssl=verify_ssl)

    if api_search_response is None or "count" not in api_search_response:
        print "[ERROR] API search request failed. [server] %s" % apimgt_url
        return False, None

    if api_search_response["count"] == 0:
        return False, "0"

    return True, api_search_response["list"][0]["id"]


def api_version_exists(api_name, api_version, apimgt_url, access_token, verify_ssl=False):
    """
    Check if the given API-Version exists
    :param api_name:
    :param api_version:
    :param apimgt_url:
    :param access_token:
    :param verify_ssl:
    :return:
    """
    query_params = {
        "query": "name:" + api_name + " " + "version:" + api_version
    }

    api_search_response = get_all_apis(apimgt_url, access_token, query_params=query_params, verify_ssl=verify_ssl)

    if api_search_response is None or "count" not in api_search_response:
        print "[ERROR] API search request failed. [server] %s" % apimgt_url
        return False, None

    if api_search_response["count"] == 0:
        return False, "0"

    if api_search_response["count"] > 1:
        print "[ERROR] Shouldn't be: %s APIs resulted in search [api-name] %s [api-version] %s\n" % (
            api_search_response["count"], api_name, api_version)

        return True, api_search_response["count"]

    return True, api_search_response["list"][0]["id"]


def create_api(api_def, apimgt_url, access_token, verify_ssl):
    req_headers = {
        "Authorization": "Bearer " + access_token.strip(),
        "Content-Type": "application/json"
    }

    successful, sc, create_response = do_post(apis_ep.format(apimgt_url, ""), req_body=api_def, req_headers=req_headers,
                                              verify_ssl=verify_ssl, json_body=True)

    if not successful:
        print "[ERROR] API Create request failed. [err] %s [status-code] %s [url] %s" % (
            create_response, sc, apis_ep.format(apimgt_url, ""))
        return False

    if not (200 < sc < 300):
        print "[ERROR] API Create request failed. [err] %s [status-code] %s [url] %s" % (
            create_response, sc, apis_ep.format(apimgt_url, ""))
        return False

    return True


def add_api_version(api_id, api_version, apimgt_url, access_token, verify_ssl=False):
    req_headers = {
        "Authorization": "Bearer " + access_token.strip()
    }

    query_params = {
        "apiId": api_id,
        "newVersion": api_version
    }

    successful, sc, create_response = do_post(api_versions_ep.format(apimgt_url), query_params=query_params,
                                              req_headers=req_headers, verify_ssl=verify_ssl)

    if not successful:
        print "[ERROR] API Version Add request failed. [err] %s [status-code] %s [url] %s" % (
            create_response, sc, api_versions_ep.format(apimgt_url, ""))
        return False

    if not (200 < sc < 300):
        print "[ERROR] API Version Add request failed. [err] %s [status-code] %s [url] %s" % (
            create_response, sc, api_versions_ep.format(apimgt_url, ""))
        return False

    return True


def update_api(api_def, apimgt_url, access_token, verify_ssl=False):
    req_headers = {
        "Authorization": "Bearer " + access_token.strip(),
        "Content-Type": "application/json"
    }

    successful, sc, api_response = do_put(apis_ep.format(apimgt_url, "/" + api_def["id"]), req_body=api_def,
                                          req_headers=req_headers, verify_ssl=verify_ssl, json_body=True)

    if not successful:
        print "[ERROR] Put:API call failed [status-code] %s [url] %s" % (
            sc, apis_ep.format(apimgt_url, "/" + api_def["id"]))
        return None

    return True
