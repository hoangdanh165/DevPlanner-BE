from rest_framework.response import Response


def success_response(data=None, message="Success", status=200):
    return Response(
        {
            "success": {
                "code": status,
                "message": message,
                "details": {
                    "data": data,
                },
            }
        }
    )


def error_response(errors=None, message="Error", status=400):
    return Response(
        {
            "error": {
                "code": status,
                "message": message,
                "details": {
                    "data": errors,
                },
            }
        }
    )
