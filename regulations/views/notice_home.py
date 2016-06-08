# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from operator import itemgetter

import logging

from django.http import Http404
from django.template.response import TemplateResponse
from django.views.generic.base import View

from regulations.generator.api_reader import ApiReader
from regulations.views.preamble import (
    notice_data, CommentState)


logger = logging.getLogger(__name__)


class NoticeHomeView(View):
    """
    Basic view that provides a list of regulations and notices to the context.
    """
    template_name = None  # We should probably have a default notice template.

    def get(self, request, *args, **kwargs):
        notices = ApiReader().notices().get("results", [])
        context = {}
        notices_meta = []

        for notice in notices:
            try:
                if notice.get("document_number"):
                    _, meta, _ = notice_data(notice["document_number"])
                    notices_meta.append(meta)
            except Http404:
                pass

        notices_meta = sorted(notices_meta, key=itemgetter("publication_date"),
                              reverse=True)

        context["notices"] = notices_meta
        # Django templates won't show contents of CommentState as an Enum, so:
        context["comment_state"] = {state.name: state.value for state in
                                    CommentState}

        template = self.template_name
        return TemplateResponse(request=request, template=template,
                                context=context)
