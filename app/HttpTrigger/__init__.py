import logging

import azure.functions as func
import requests

from python_extension_timer_header import PythonExtensionTimerHeader
PythonExtensionTimerHeader.configure(append_to_http_response=True)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    domain = req.params.get('domain', '')
    repeat = int(req.params.get('repeat', '0'))

    if domain and repeat:
        for _ in range(repeat):
            requests.get(f'https://{domain}')
        return func.HttpResponse(f"Url: https://{domain}, Repeated: {repeat}")
    else:
        return func.HttpResponse(
            "Please let me know which site to visit ?domain=microsoft.com&repeat=5",
            status_code=200
        )
