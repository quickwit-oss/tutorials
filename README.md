# Tutorials

## Tracing

### Setup

1. Clone the repository and go to the tracing directory

2. Create a virtual environment

```bash
python3 -m venv . && source ./bin/activate
```

3. Install python dependencies

```bash
pip install flask
# Installs the API, SDK, and the opentelemetry-bootstrap and opentelemetry-instrument tools
pip install opentelemetry-distro 
# Tool for automatic instrumentation.
opentelemetry-bootstrap -a install
```

4. Install Quickwit and start a server

```bash
curl -L https://install.quickwit.io | sh
cd quickwit-*
./quickwit run
```

### Auto-instrumentation

Start your app with `my_instrumented_app` script.

```bash
OTEL_METRICS_EXPORTER=none \ # We don't need metrics
OTEL_SERVICE_NAME=my_app \
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://localhost:7281 \
opentelemetry-instrument python my_instrumented_app.py
```

Now hit the endpoint [`http://localhost:5000/process-ip`](http://localhost:5000/process-ip), it will send traces to Quickwit.

### Manual instrumentation

Start your app with `my_manually_instrumented_app` script.

```bash
python my_manually_instrumented_app.py
```

Now hit the endpoint [`http://localhost:5000/process-ip`](http://localhost:5000/process-ip), it will send traces to Quickwit.
