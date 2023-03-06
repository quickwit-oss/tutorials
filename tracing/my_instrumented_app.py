import random
import time
import requests

from flask import Flask

from opentelemetry import trace

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer(__name__)

app = Flask(__name__)

@app.route("/process-ip")
@tracer.start_as_current_span("process_ip")
def process_ip():
    body = fetch()
    ip = parse(body)
    display(ip)
    return ip

@tracer.start_as_current_span("fetch")
def fetch():
    resp = requests.get('https://httpbin.org/ip')
    body = resp.json()

    headers = resp.headers
    current_span = trace.get_current_span()
    current_span.set_attribute("status_code", resp.status_code)
    current_span.set_attribute("content_type", headers["Content-Type"])
    current_span.set_attribute("content_length", headers["Content-Length"])

    return body

@tracer.start_as_current_span("parse")
def parse(body):
    # Sleep for a random amount of time to make the span more visible.
    secs = random.randint(1, 100) / 1000
    time.sleep(secs)

    return body["origin"]

@tracer.start_as_current_span("display")
def display(ip):
    # Sleep for a random amount of time to make the span more visible.
    secs = random.randint(1, 100) / 1000
    time.sleep(secs)

    message = f"Your IP address is `{ip}`."
    print(message)

    current_span = trace.get_current_span()
    current_span.add_event(message)

if __name__ == "__main__":
    app.run(port=5000)
