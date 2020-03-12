import requests

data = {
  "price": 1,
  "network": "mtn",
  "recipient_number": "0260000000",
  "sender": "0247915505",
  "option": "rmta",
  "apikey": "3715f15a4738e761c39abf9e655bf464bb0861d1",
  "orderID": "1234567"
}

url = 'https://client.teamcyst.com/api_call.php'

headers = {'Content-Type':'application/json'}
response = requests.post(url, data=data, headers=headers)
print(response.content)

