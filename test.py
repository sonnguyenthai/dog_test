# Simple test
import requests, base64, json

data = {
    "name" : "Rex 5",
    "image": base64.b64encode(open('/Users/wisekey/Pictures/1375583065-vyoanh-6.jpg', 'rb').read())}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
r = requests.put("http://localhost:8080/dog/1", data=json.dumps(data), headers=headers)
print r.text