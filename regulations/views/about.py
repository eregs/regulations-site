from django.http import HttpResponse
from django.template.loader import select_template


def about(request):
    t = select_template([
        'regulations/custom-about.html',
        'regulations/about.html'])
    return HttpResponse(t.render({}, request))
