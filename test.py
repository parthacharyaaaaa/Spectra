import requests
from requests import Response

# response : Response = requests.post("http://192.168.0.106:5000/urls", json={"url" : "https://www.youtube.com/watch?v=clJCDHml2cA"})
response : Response = requests.get("http://192.168.0.106:5000/videos/357729e9881d456bb9b79f9e92ecb117/process")
print(response.text)