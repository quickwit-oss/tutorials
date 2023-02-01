import ipaddress
import random
import time

import requests

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

# Service name is required for most backends,
# and although it's not necessary for console export,
# it's good to set service name anyways.
resource = Resource(attributes={
    SERVICE_NAME: "my_ip"
})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
processor = BatchSpanProcessor(
    OTLPSpanExporter(endpoint="localhost:7281", insecure=True))
provider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer(__name__)


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


@tracer.start_as_current_span("run")
def run():
    body = fetch()
    ip = parse(body)
    display(ip)


if __name__ == "__main__":
    run()
