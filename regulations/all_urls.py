from django.conf.urls import include, url

from regulations.urls import urlpatterns

urlpatterns = [
    url(r'^comments/', include('notice_comment.urls')),
] + urlpatterns
