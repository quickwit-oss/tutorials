import random
import time
import requests

from flask import Flask

app = Flask(__name__)

@app.route("/process-ip")
def process_ip():
    body = fetch()
    ip = parse(body)
    display(ip)
    return ip

def fetch():
    resp = requests.get('https://httpbin.org/ip')
    body = resp.json()
    return body

def parse(body):
    # Sleep for a random amount of time to make the span more visible.
    secs = random.randint(1, 100) / 1000
    time.sleep(secs)

    return body["origin"]

def display(ip):
    # Sleep for a random amount of time to make the span more visible.
    secs = random.randint(1, 100) / 1000
    time.sleep(secs)

    message = f"Your IP address is `{ip}`."
    print(message)

if __name__ == "__main__":
    app.run(port=5000)
