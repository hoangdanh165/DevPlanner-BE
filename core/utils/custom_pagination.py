from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 5
    page_query_param = "page"
    max_page_size = 10


class CustomPaginationProject(PageNumberPagination):
    page_size = 5
    page_query_param = "page"
    max_page_size = 10
