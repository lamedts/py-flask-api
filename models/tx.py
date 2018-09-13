from pymongo import MongoClient

# MongoDB
conn = MongoClient("127.0.0.1")
db = conn.coll
collection = db.orders

def get_orders(key, value):
    collection.stats
    cursor = collection.find({ key: value }, projection={'_id': False})
    data = [d for d in cursor]
    return data

def get_order(key, value):
    collection.stats
    cursor = collection.find_one({ key: value }, projection={'_id': False})
    return cursor

def insert_order(order):
    collection.stats
    collection.insert_one(order)

def update_order(order, request_id):
    collection.stats
    collection.find_one_and_update({ 'request_id': request_id }, { '$set': order })