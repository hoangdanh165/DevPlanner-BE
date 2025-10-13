from rest_framework.views import exception_handler
from utils.response import error_response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return error_response(
            message=(
                "Validation failed" if response.status_code == 400 else "Error occurred"
            ),
            errors=response.data,
            status=response.status_code,
        )
    else:
        return error_response(message=str(exc), errors=None, status=500)
