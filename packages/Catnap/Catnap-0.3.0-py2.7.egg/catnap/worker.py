from __future__ import absolute_import, division, print_function, with_statement, unicode_literals

import catnap
import requests

# Python2/3 compatible way of coercing values to unicode via str()
try:
    str = unicode
except NameError:
    pass

def execute_testcase(testcase, session=None, request_options={}):
    """
    Executes a testcase
    """

    # Construct a new session if one has not been provided, whose scope will#
    # only last through this testcase
    if not session:
        session = requests.Session()

    # Set a default User-Agent (this can be overriden by user options)
    headers = {
        "User-Agent": "Catnap %s" % catnap.version
    }

    headers.update(testcase.headers)

    # Build the request
    request = requests.Request(
        testcase.method, testcase.url,
        headers=headers,
        data=testcase.body,
        params=testcase.query_params,
        auth=testcase.auth
    ).prepare()

    # Create a context for sharing with testcase-specified python code
    context = dict(request=request, response=None, session=session, testcase=testcase)

    # Within this `with` block, stdout/stderr will be replaced and buffered
    # to a string for later output. Errors will be caught for display.
    with catnap.TestcaseResult() as result:
        # Run the `on_request` code if specified
        if testcase.on_request:
            exec(testcase.on_request, context)

        # Get the response
        response = session.send(request, **request_options)
        context["response"] = response

        # Validate the response code
        if testcase.code:
            assert response.status_code == testcase.code, "Expected code %s, but got code %s" % (testcase.code, response.status_code)

        # Validate the response (redirected) URL
        if testcase.response_url:
            assert response.url == testcase.response_url, "Expected to be redirected to URL %s, but got %s" % (testcase.response_url, response.url)

        # Validate the response headers
        for key, value in testcase.response_headers.items():
            actual_value = response.headers.get(key)
            assert actual_value != None, "Expected header %s is missing" % key
            assert actual_value == value, "Expected header %s to be %s, but got %s" % (key, value, actual_value)

        # Validate the response body
        if testcase.response_body_type:
            # Run assertions on different parts of the response based on the
            # provided expected response body. JSON is compared against
            # serialized data structures; base64-encoded is compared against a
            # binary version of the response body; everything else is compared
            # to a plaintext version of the response body.
            if testcase.response_body_type == "json_response_body":
                assert response.json() == testcase.response_body
            elif testcase.response_body_type == "base64_response_body":
                assert response.content == testcase.response_body
            else:
                assert response.text == testcase.response_body

        # Run the `on_response` code if specified
        if testcase.on_response:
            exec(testcase.on_response, context)

    return result
