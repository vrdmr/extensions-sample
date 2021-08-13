import logging

import azure.functions as func
import requests

from python_extension_validator import PythonExtensionValidator, QueryparamType
from opencensus.extension.azure.functions import OpenCensusExtension
from opencensus.trace import config_integration

# Function Level Extension
PythonExtensionValidator(__file__, validate={
    'domain': QueryparamType.String,
    'repeat': QueryparamType.Int
})

# App Level Extension
config_integration.trace_integrations(['requests'])
OpenCensusExtension.configure()

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    if not context.is_valid:
        return func.HttpResponse(
            "Please let me know which site to visit ?domain=microsoft.com&repeat=5\n" +
            context.error_messages,
            status_code=200
        )

    with context.tracer.span("parent"):
        for _ in range(context.repeat):
            requests.get(f'https://{context.domain}')

    return func.HttpResponse(f"Url: https://{context.domain}, Repeated: {context.repeat}")
