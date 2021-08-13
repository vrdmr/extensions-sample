import logging

import azure.functions as func
import requests

from python_extension_validator import PythonExtensionValidator, QueryparamType

PythonExtensionValidator(__file__, validate={
    'domain': QueryparamType.String,
    'repeat': QueryparamType.Int
})

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    if not context.is_valid:
        return func.HttpResponse(
            "Please let me know which site to visit ?domain=microsoft.com&repeat=5\n" +
            context.error_messages,
            status_code=200
        )

    for _ in range(context.repeat):
        requests.get(f'https://{context.domain}')
    return func.HttpResponse(f"Url: https://{context.domain}, Repeated: {context.repeat}")
