from rest_framework.response import Response


def success_response(data=None, message="Success", status=200):
    return Response(
        {"status": status, "message": message, "errors": None, "data": data},
        status=status,
    )


def error_response(message="Error", errors=None, status=400):
    return Response(
        {"status": status, "message": message, "errors": errors, "data": None},
        status=status,
    )
