# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import sys
from datetime import datetime,timezone
if sys.version_info[0] <= 2:
	from httplib import HTTPSConnection
else:
	from http.client import HTTPSConnection

# endpoint = "https://ssl.tencentcloudapi.com"

class TencentApi:
	def __init__(self, secret_id:str, secret_key:str, token:str, service:str, host:str, region:str, version:str):
		self.secret_id = secret_id
		self.secret_key = secret_key
		self.token = token
		self.service = service
		self.host = host
		self.region = region
		self.version = version

	def send(self,action:str, params:dict):
		secret_id=self.secret_id
		secret_key=self.secret_key
		token=self.token
		service=self.service
		host=self.host
		region=self.region
		version=self.version

		algorithm = "TC3-HMAC-SHA256"
		payload=json.dumps(params)
		def sign(key:str, msg:str):
			return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()
		
		timestamp = int(datetime.now(timezone.utc).timestamp())
		date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")

		# ************* 步骤 1：拼接规范请求串 *************
		http_request_method = "POST"
		canonical_uri = "/"
		canonical_querystring = ""
		ct = "application/json; charset=utf-8"
		canonical_headers = "content-type:%s\nhost:%s\nx-tc-action:%s\n" % (ct, host, action.lower())
		signed_headers = "content-type;host;x-tc-action"
		hashed_request_payload = hashlib.sha256(payload.encode("utf-8")).hexdigest()
		canonical_request = (http_request_method + "\n" +
							canonical_uri + "\n" +
							canonical_querystring + "\n" +
							canonical_headers + "\n" +
							signed_headers + "\n" +
							hashed_request_payload)

		# ************* 步骤 2：拼接待签名字符串 *************
		credential_scope = date + "/" + service + "/" + "tc3_request"
		hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
		string_to_sign = (algorithm + "\n" +
						str(timestamp) + "\n" +
						credential_scope + "\n" +
						hashed_canonical_request)

		# ************* 步骤 3：计算签名 *************
		secret_date = sign(("TC3" + secret_key).encode("utf-8"), date)
		secret_service = sign(secret_date, service)
		secret_signing = sign(secret_service, "tc3_request")
		signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

		# ************* 步骤 4：拼接 Authorization *************
		authorization = (algorithm + " " +
						"Credential=" + secret_id + "/" + credential_scope + ", " +
						"SignedHeaders=" + signed_headers + ", " +
						"Signature=" + signature)

		# ************* 步骤 5：构造并发起请求 *************
		headers = {
			"Authorization": authorization,
			"Content-Type": "application/json; charset=utf-8",
			"Host": host,
			"X-TC-Action": action,
			"X-TC-Timestamp": timestamp,
			"X-TC-Version": version
		}
		if region:
			headers["X-TC-Region"] = region
		if token:
			headers["X-TC-Token"] = token

		try:
			req = HTTPSConnection(host)
			req.request("POST", "/", headers=headers, body=payload.encode("utf-8"))
			resp = req.getresponse()
			resjson=json.loads(resp.read().decode("utf-8"))
			if "Error" in resjson["Response"]:
				print(json.dumps(resjson["Response"], indent=4, ensure_ascii=False))
				exit(1)
				return None
			return resjson
		except Exception as err:
			print(err)
			exit(1)

