from rest_framework.response import Response


def success_response(
    data=None,
    message="Success",
    status=200,
    meta=None,
):
    response_data = {
        "success": True,
        "message": message,
        "data": data,
    }

    if meta:
        response_data["meta"] = meta

    return Response(response_data, status=status)


def error_response(errors=None, message="Error", status=400):
    response_data = {
        "error": {
            "message": message,
            "details": {
                "data": errors,
            },
        }
    }
    return Response(data=response_data, status=status)
