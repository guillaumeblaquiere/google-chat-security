import os

from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)


# Endpoint for the private exposition of Cloud Run. No additional security check because IAM and Google infrastructure
# (gfe) already did the job. Do not use this endpoint publicly
@app.route('/private', methods=["POST"])
def private():
    # get the request body in JSON format
    body = request.get_json()
    dict_response = {"text": f'Echo is: {process_message(body)}'}
    return jsonify(dict_response), 200


def process_message(body):
    return body.get("message").get("text")

# Log the headers and the body of any HTTP requests made on the service.
@app.route('/log', methods=["POST", "GET", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
def log():
    print("The resquet hearders are:")
    print(request.headers)
    print("The resquet body is:")
    print(request.get_data().decode("UTF-8"))
    return '', 200


# Current project Number where the Google Chat API is configured.
projectNumber = os.getenv("PROJECT_NUMBER")
# The URL where the public keys of the Google Chat service account signature are.
jwks_url = "https://www.googleapis.com/service_accounts/v1/metadata/jwk/chat%40system.gserviceaccount.com"


# Check the HTTP request
# Get the Authorization header value, must start by Bearer
# Extract the JWT token, get the JWK and validate the signature and the audience (i.e. the projectNumber)
# Return true if the check passed
# Return false with the error string if failed.
def check_request(request):
    request_token = request.headers.get('Authorization')
    if request_token:
        try:
            # remove bearer prefix
            request_token = request_token[len("Bearer "):]
            # Check if the token is valid
            decode_and_validate_token(request_token)
            return True, ""
        except Exception as error:
            print(error)
            return False, str(error)
    return False, "No authorization in the request header"


# Based on a JWT Token, get the JWK and validate the signature and the audience (i.e. the projectNumber)
# Return the decoded token if valid, else an exception.
def decode_and_validate_token(token):
    jwks_client = jwt.PyJWKClient(jwks_url)
    header = jwt.get_unverified_header(token)
    key = jwks_client.get_signing_key(header["kid"]).key
    return jwt.decode(token, key, [header["alg"]], audience=projectNumber)

# Endpoint for the public exposition of Cloud Run. A security check is required
@app.route('/public', methods=["POST"])
def public():
    # Check the request validity
    valid, err = check_request(request)
    if not valid:
        dict_response = {"text": f'Technical error: {err}'}
        return jsonify(dict_response), 200

    # Because the request is valid, the processing can continue
    body = request.get_json()
    dict_response = {"text": f'Echo is: {process_message(body)}'}
    return jsonify(dict_response), 200


# For execution
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
