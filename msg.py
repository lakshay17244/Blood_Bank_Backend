import requests

token = 'Token xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

def send_otp(numb):
	url = "https://d7networks.com/api/verifier/send"
	payload = {'mobile': numb,
	'sender_id': 'SMSINFO',
	'message': 'Your otp code is {code}',
	'expiry': '900'}
	files = [

	]
	headers = {
	  'Authorization': token
	}
	response = requests.request("POST", url, headers=headers, data = payload, files = files)
	verify_id  = response.json()["otp_id"]

	print(response.json())
	return verify_id

def check_otp(otp_rec,verify_id):
	url = "https://d7networks.com/api/verifier/verify"
	payload = {'otp_id': verify_id,
	'otp_code': otp_rec}

	print(payload)

	files = [

	]
	headers = {
	  'Authorization': token
	}

	response = requests.request("POST", url, headers=headers, data = payload, files = files)

	print(response.text.encode('utf8'))
	return response.json()

numb = '+919654xxxxxx'
vid = send_otp(numb)
otp = input()
print(check_otp(otp,vid))

