
import sys, os, base64, datetime, hashlib, hmac 
import requests # pip install requests
import config.config as credit

def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

def getSignatureKey(key, date_stamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), date_stamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning

def requestPrepare(endpoint, host, path, body):
    predefine_header = {
        'Accept': 'application/json',
        'Host': 'testgateway.uat-activesg.com',
        'Cache-control': 'no-cache',
        'User-Agent': 'python-requests/2.9.1',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    request_parameters = body
    endpoint = endpoint
    host = host
    canonical_uri = path

    method = 'POST'
    service = credit.aws_service_name
    region = credit.aws_region
    access_key = credit.aws_access_key
    secret_key = credit.aws_secret_key
    xapikey = credit.xapikey
    t = datetime.datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope

    # prepare canonical_request
    headers = {**predefine_header, 'X-Amz-Date':amz_date, 'x-api-key':xapikey}
    canonical_querystring = ''
    canonical_headers = ''
    signed_headers = ''
    for k in sorted(headers.keys()):
        canonical_headers  = canonical_headers + '%s:%s\n' % (k.lower(), headers[k])
        signed_headers = signed_headers + '%s;' % (k.lower())
    signed_headers = signed_headers[:-1]
    # signed_headers = 'accept;cache-control;host;user-agent;x-amz-date;x-api-key'
    payload_hash = hashlib.sha256(request_parameters.encode('utf-8')).hexdigest()
    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash

    # prepare string_to_sign
    signing_key = getSignatureKey(secret_key, date_stamp, region, service)
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = date_stamp + '/' + region + '/' + service + '/' + 'aws4_request'
    string_to_sign = algorithm + '\n' +  amz_date + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    
    # generate authorization_header
    signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
    authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature

    return {**headers, 'Authorization':authorization_header}

