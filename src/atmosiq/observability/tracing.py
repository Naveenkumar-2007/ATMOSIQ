from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def init_tracing(service_name="atmosiq", exporter=None):
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    if exporter is not None:
        provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)


def get_tracer(service_name="atmosiq"):
    return trace.get_tracer(service_name)


class span_ctx:
    def __init__(self, name, attributes=None):
        self.name = name
        self.attributes = attributes or {}
        self.tracer = get_tracer()

    def __enter__(self):
        self.span = self.tracer.start_span(self.name)
        for k, v in self.attributes.items():
            self.span.set_attribute(k, str(v))
        return self.span

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            self.span.record_exception(exc)
            self.span.set_status(trace.StatusCode.ERROR, str(exc))
        self.span.end()
        return False
