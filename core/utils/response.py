from rest_framework.response import Response


def success_response(
    data=None,
    message="Success",
    status=200,
    meta=None,
):
    """
    Chuẩn hóa format API response cho toàn hệ thống.
    - data: dữ liệu chính (list, dict, ...).
    - meta: thông tin phụ (pagination, filters, stats...).
    """
    response_data = {
        "success": True,
        "code": status,
        "message": message,
        "data": data,
    }

    if meta:
        response_data["meta"] = meta

    return Response(response_data, status=status)


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
