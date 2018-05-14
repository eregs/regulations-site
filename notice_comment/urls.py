from django.conf.urls import url

from notice_comment.views import (PrepareCommentView, SubmitCommentView,
                                  get_federal_agencies, get_gov_agency_types,
                                  preview_comment, upload_proxy)

urlpatterns = [
    url(r'^attachment$', upload_proxy),
    url(r'^review/(?P<doc_number>[\w-]+)$', PrepareCommentView.as_view(),
        name='comment_review'),
    url(r'^preview$', preview_comment),
    url(r'^(?P<doc_number>[\w-]+)$', SubmitCommentView.as_view(),
        name='comment_submit'),
    url(r'^federal_agencies$', get_federal_agencies),
    url(r'^gov_agency_types$', get_gov_agency_types),
]
