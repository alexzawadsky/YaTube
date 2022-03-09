from django.core.paginator import Paginator
from yatube.settings import PAGINATOR_OBJECTS_ON_PAGE


def paginator(request, objects, *args):
    paginator = Paginator(objects, PAGINATOR_OBJECTS_ON_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return page_obj
