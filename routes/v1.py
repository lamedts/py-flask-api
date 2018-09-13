import utils.aws_sign as aws_sign
import utils.hash_sign as hash_sign
import json
import base64
import requests
import config.config as credit

from werkzeug.local import LocalProxy
from flask import current_app, jsonify
logger = LocalProxy(lambda: current_app.logger)

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
# client = MongoClient('mongodb://localhost:27017/')
db = client['db']
col = db['col']

def query(order):
    retrieved_order = col.find_one({"trans_id": order['trans_id']})
    if retrieved_order and 'trans_status' in retrieved_order:
        if retrieved_order['trans_status'] == 'complete':
            return {"msg": "ok", "status_code": 10}
        else:
            logger.info('retrieved_order: %s' % retrieved_order)
            return {"msg": "ok", "status_code": 1}
    return {"msg": "no record", "status_code": 0}

def update(jwt):
    logger.info("%s" % jwt)
    data = jwt.split('.')
    # payload = base64.urlsafe_b64decode(data[1])
    payload = json.loads(base64.urlsafe_b64decode(data[1] + '=' * (-len(data[1]) % 4)).decode())
    # insert_id = col.insert_one(payload).inserted_id
    result = col.replace_one({"trans_id": payload['trans_id']}, payload, upsert=True); 
    if result.modified_count < 1 and result.matched_count < 1 and result.upserted_id == None:
        logger.error("Got jwt but cant insert to db")
    return {"status_code": 0, "msg": "ok"}

def inital(order):
    # todo: verify data before process
    header = {"typ":"JWT","alg":"RS256"}
    payload = {
        "partner_id": "SR0001",
        "request_id": order['request_id'], # "6f81fafa-4d0e-4829-94d0-b349d58506b3"
        "terminal_id":"terminal_id", # 
        "branch_id" :"branch_id", # 
        "trans_id": order['trans_id'], # 20180201TR000001
        "trans_datetime": order['ts'], # '2005-08-15T15:52:01+00:00'
        "description": order['desc'], # 'Lorem ipsum labore in.'
        "amount": order['amount'], # 26.5
        "redirect_uri": "%s/api/v1/update" % credit.callback_host
    }
    sheader = json.dumps(header).replace(": ", ":").replace(', ', ',')
    spayload = json.dumps(payload).replace(": ", ":").replace(', ', ',')
    data = '%s.%s' % (base64.urlsafe_b64encode(sheader.encode('utf-8')).decode("utf-8") , base64.urlsafe_b64encode(spayload.encode('utf-8')).decode("utf-8") )
    b64_signed = hash_sign.sign_data("config/key/privky.pem", data)
    jwt = '%s.%s' % (data, b64_signed.decode("utf-8"))

    endpoint = ''
    path = '/merchant/transaction/initiate'
    body2 = 'version=v1&request=' + jwt
    host = 'host.com'
    headers = aws_sign.requestPrepare(endpoint, host, path, body2)
    r = requests.post(endpoint, data=body2, headers=headers)

    # print(r)
    msg = json.loads(r.text)
    if 'data' in msg:
        msg_ary = msg['data'].split('.')
        res_payload = msg_ary[1]
        data = json.loads(base64.urlsafe_b64decode(res_payload + '=' * (-len(res_payload) % 4)).decode('utf-8'))
        for key in data:
            if key == 'qr_code':
                logger.info('got qrcode: %s' % data)
                return {"qrcode": data[key], "msg":"ok", "status_code": 11}
            if data['status_code'] == 'ERROR':
                logger.error('error when got qrcode: %s' % data)
                return {"qrcode": '', "msg":data['message'], "status_code": 1}
    else:
        logger.warn('%s [%s]' % (msg['message'], r.text))
        return {"msg": msg['message'], "status_code": 0}
