from Crypto.PublicKey import RSA 
from Crypto.Signature import PKCS1_v1_5 
from Crypto.Hash import SHA256 
import base64

def sign_data(private_key_loc, data):
	'''
	param: private_key_loc Path to your private key
	param: data = base64urlEncode(header) + "." + base64url(payload))
	return: base64 encoded signature
	'''
	key = open(private_key_loc, "r").read() 
	rsakey = RSA.importKey(key) 
	signer = PKCS1_v1_5.new(rsakey) 
	digest = SHA256.new() 
	digest.update(data.encode()) 
	sign = signer.sign(digest) 
	return base64.urlsafe_b64encode(sign)

def verify_sign(public_key_loc, signature, data):
	pub_key = open(public_key_loc, "r").read() 
	rsakey = RSA.importKey(pub_key) 
	signer = PKCS1_v1_5.new(rsakey) 
	digest = SHA256.new() 
	digest.update(data.encode()) 
	if signer.verify(digest, base64.urlsafe_b64decode(signature)):
		return True
	return False
