import os
os.environ['http_proxy'] = "192.168.5.8:3128"
os.environ['https_proxy'] = "192.168.5.8:3128"

print("http_proxy:", os.environ.get('http_proxy'))
print("https_proxy:", os.environ.get('https_proxy'))
