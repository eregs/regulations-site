# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from collections import namedtuple
from copy import deepcopy
from datetime import date
from enum import Enum

import logging

from django.http import Http404
from django.conf import settings
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
from django.views.generic.base import View

from fr_notices import navigation
from regulations import docket
from regulations.generator import generator
from regulations.generator.api_reader import ApiReader
from regulations.generator.html_builder import (
    CFRChangeHTMLBuilder, PreambleHTMLBuilder)
from regulations.generator.layers.utils import (
    convert_to_python, is_contained_in)
from regulations.views import chrome, error_handling, utils
from regulations.views.diff import Versions


logger = logging.getLogger(__name__)


class CommentState(Enum):
    NO_COMMENT, PREPUB, OPEN, CLOSED = range(4)


def find_subtree(root, label_parts):
    """Given a nested tree and a label to look for, find the associated node
    in the tree. Note that, unlike regulations, preamble trees _always_ encode
    their exact position in the tree."""
    cursor = root
    while cursor and cursor['label'] != label_parts:
        next_cursor = None
        for child in cursor['children']:
            if child['label'] == label_parts[:len(child['label'])]:
                next_cursor = child
        cursor = next_cursor
    return cursor


def generate_html_tree(subtree, request, id_prefix=None):
    """Use the HTMLBuilder to generate a version of this subtree with
    appropriate markup. Currently, includes no layers"""
    doc_id = '-'.join(subtree['label'])
    layers = list(generator.layers(
        utils.layer_names(request), 'preamble', doc_id, sectional=True))
    builder = PreambleHTMLBuilder(layers, id_prefix=id_prefix,
                                  index_prefix=[0, subtree.get('lft')])
    builder.tree = subtree
    builder.generate_html()

    return {'node': builder.tree,
            'markup_page_type': 'reg-section'}


def merge_cfr_changes(doc_number, notice):
    """We started with a mock version of these changes which were stored as a
    setting, CFR_CHANGES. Until we remove that completely, merge those values
    with real data from the notice structure"""
    mock_notice = getattr(settings, 'CFR_CHANGES', {}).get(doc_number) or {}

    versions = dict(mock_notice.get('versions', {}))        # copy
    versions.update(notice.get('versions', {}))

    amendments = list(mock_notice.get('amendments', []))    # copy
    amendments.extend(notice.get('amendments', []))

    return versions, amendments


def notice_data(doc_number):
    preamble = ApiReader().preamble(doc_number.replace('-', '_'))
    if preamble is None:
        raise Http404

    notice = ApiReader().notice(doc_number.replace('_', '-')) or {}

    fields = (
        "amendments",
        "cfr_parts",
        "cfr_title",
        "comment_doc_id",
        "comments_close",
        "dockets",
        "document_number",
        "effective_on",
        "footnotes",
        "fr_citation",
        "fr_url",
        "fr_volume",
        "meta",
        "primary_agency",
        "primary_docket",
        "publication_date",
        "regulation_id_numbers",
        "section_by_section",
        "supporting_documents",
        "title",
        "versions"
    )

    meta = {}
    for field in fields:
        if field in notice:
            meta[field] = convert_to_python(deepcopy(notice[field]))

    # If there's no metadata, fall back to getting it from settings:
    if not meta:
        meta = getattr(settings, 'PREAMBLE_INTRO', {}).get(doc_number, {}).get(
            'meta', {})
        meta = convert_to_python(deepcopy(meta))

    today = date.today()
    if 'comments_close' in meta and 'publication_date' in meta:
        close_date = meta['comments_close'].date()
        publish_date = meta['publication_date'].date()
        if today < publish_date:
            meta['comment_state'] = CommentState.PREPUB
        elif today <= close_date:
            meta['comment_state'] = CommentState.OPEN
            meta['days_remaining'] = 1 + (close_date - today).days
        else:
            meta['comment_state'] = CommentState.CLOSED
    else:
        meta['comment_state'] = CommentState.NO_COMMENT

    # We don't pass along cfr_ref information in a super useful format, yet.
    # Construct one here:
    if 'cfr_refs' not in meta and 'cfr_title' in meta and 'cfr_parts' in meta:
        meta['cfr_refs'] = [{"title": meta['cfr_title'],
                             "parts": meta['cfr_parts']}]

    return preamble, meta, notice


def first_preamble_section(preamble):
    return next(
        (
            node for node in preamble['children']
            if not node['label'][-1].startswith('p')
        ),
        None,
    )


def common_context(doc_number):
    """All of the "preamble" views share common context, such as preamble
    data, toc info, etc. This function retrieves that data and returns the
    results as a dict. This may throw a 404"""
    preamble, meta, notice = notice_data(doc_number)
    preamble_toc = navigation.make_preamble_nav(preamble['children'])
    versions, amendments = merge_cfr_changes(doc_number, notice)
    cfr_toc = navigation.make_cfr_change_nav(doc_number, versions, amendments)

    return {
        'cfr_change_toc': cfr_toc,
        'doc_number': doc_number,
        'meta': meta,
        'notice': notice,
        'preamble': preamble,
        'preamble_toc': preamble_toc,
    }


class PreambleView(View):
    """Displays either a notice preamble (or a subtree of that preamble). If
    using AJAX or specifically requesting, generate only the preamble markup;
    otherwise wrap it in the appropriate "chrome" """
    def get(self, request, *args, **kwargs):
        label_parts = kwargs.get('paragraphs', '').split('/')
        doc_number = label_parts[0]
        context = common_context(doc_number)

        # Redirect to first section on top-level preamble
        if len(label_parts) == 1:
            section = first_preamble_section(context['preamble'])
            if not section:
                raise Http404
            return redirect(
                'chrome_preamble', paragraphs='/'.join(section['label']))

        subtree = find_subtree(context['preamble'], label_parts)
        if subtree is None:
            raise Http404

        sub_context = generate_html_tree(subtree, request,
                                         id_prefix=[doc_number, 'preamble'])
        template = sub_context['node']['template_name']
        nav = navigation.footer(
            context['preamble_toc'],
            context['cfr_change_toc'],
            full_id=sub_context['node']['full_id'],
        )
        sub_context['meta'] = context['meta']

        context.update({
            'sub_context': sub_context,
            'sub_template': template,
            'full_id': sub_context['node']['full_id'],
            'section_label': sub_context['node']['human_label'],
            'type': 'preamble',
            'navigation': nav,
        })

        if not request.is_ajax() and request.GET.get('partial') != 'true':
            template = 'regulations/preamble-chrome.html'
        else:
            template = 'regulations/preamble-partial.html'
        return TemplateResponse(request=request, template=template,
                                context=context)


class ChromePreambleSearchView(chrome.ChromeSearchView):
    template_name = 'regulations/chrome-preamble-search.html'

    def get_context_data(self, **kwargs):
        label_parts = kwargs.get('label_id', '').split('/')
        doc_number = label_parts[0]
        context = common_context(doc_number)
        context['doc_type'] = 'preamble'
        context['label_id'] = kwargs.get('label_id', '')

        subtree = find_subtree(context['preamble'], label_parts)
        if subtree is None:
            raise Http404

        context.update(generate_html_tree(context['preamble'], self.request,
                                          id_prefix=[doc_number, 'preamble']))
        self.add_main_content(context)
        return context


class PrepareCommentView(View):
    def get(self, request, doc_number):
        context = common_context(doc_number)

        if context['meta']['comment_state'] != CommentState.OPEN:
            raise Http404("Cannot comment on {}".format(doc_number))

        context.update(generate_html_tree(context['preamble'], request,
                                          id_prefix=[doc_number, 'preamble']))
        context['comment_mode'] = 'write'
        context['comment_fields'] = docket.safe_get_document_fields(
            settings.COMMENT_DOCUMENT_ID)
        template = 'regulations/comment-review-chrome.html'

        return TemplateResponse(request=request, template=template,
                                context=context)


SubpartInfo = namedtuple('SubpartInfo', ['letter', 'title', 'urls', 'idx'])


# @todo - this shares a lot of code w/ PreambleView. Can we merge them?
class CFRChangesView(View):
    def get(self, request, doc_number, section):
        context = common_context(doc_number)
        full_id = '{}-cfr-{}'.format(doc_number, section)

        versions, amendments = merge_cfr_changes(doc_number, context['notice'])
        label_parts = section.split('-')

        if len(label_parts) == 1:
            sub_context = self.authorities_context(
                amendments, cfr_part=section)
            section_label = 'Authority'
        else:
            toc_position = next(
                idx for idx, nav in enumerate(context['cfr_change_toc'])
                if nav.section_id == full_id)
            sub_context = self.regtext_changes_context(
                amendments,
                versions,
                doc_number=doc_number,
                label_id=section,
                toc_position=toc_position,
            )
            section_label = sub_context['tree']['human_label']
        sub_context['meta'] = context['meta']

        context.update({
            'sub_context': sub_context,
            'sub_template': 'regulations/cfr_changes.html',
            'full_id': full_id,
            'section_label': section_label,
            'type': 'cfr',
            'navigation': navigation.footer(
                context['preamble_toc'],
                context['cfr_change_toc'],
                full_id
            ),
        })

        if not request.is_ajax() and request.GET.get('partial') != 'true':
            template = 'regulations/preamble-chrome.html'
        else:
            template = 'regulations/preamble-partial.html'
        return TemplateResponse(request=request, template=template,
                                context=context)

    @staticmethod
    def authorities_context(amendments, cfr_part):
        """What authorities information is relevant to this CFR part?"""
        relevant = [amd for amd in amendments
                    if amd.get('cfr_part') == cfr_part and 'authority' in amd]
        return {'instructions': [a['instruction'] for a in relevant],
                'authorities': [a['authority'] for a in relevant]}

    @classmethod
    def regtext_changes_context(cls, amendments, version_info, label_id,
                                doc_number, toc_position):
        """Generate diffs for the changed section"""
        cfr_part = label_id.split('-')[0]
        relevant = []
        for amd in amendments:
            changes = amd.get('changes', [])
            keys = {change[0] for change in changes}
            if any(is_contained_in(key, label_id) for key in keys):
                relevant.append(amd)

        versions = Versions(version_info[cfr_part]['left'],
                            version_info[cfr_part]['right'])
        left_tree = ApiReader().regulation(label_id, versions.older)
        diff_applier = generator.get_diff_applier(
            label_id, versions.older, versions.newer)
        if diff_applier is None:
            raise error_handling.MissingContentException()

        layers = list(generator.diff_layers(versions, label_id))

        builder = CFRChangeHTMLBuilder(
            layers, diff_applier, id_prefix=[str(doc_number), 'cfr'],
            index_prefix=[1, toc_position]
        )
        builder.tree = left_tree or {}
        builder.generate_html()

        return {
            'instructions': [a['instruction'] for a in relevant],
            'subparts': list(cls.subpart_changes(doc_number, relevant,
                                                 label_id)),
            'tree': builder.tree,
        }

    @staticmethod
    def subpart_changes(doc_number, amendments, label_id):
        """Meta data about additional subparts; we'll pass this through to the
        template"""
        subpart_changes = [change['node']
                           for amd in amendments
                           for key, change_list in amd.get('changes', [])
                           for change in change_list
                           if 'Subpart' in key]
        for change in subpart_changes:
            urls = [
                reverse('cfr_changes',
                        kwargs={'doc_number': doc_number, 'section': section})
                for section in change['child_labels']]
            yield SubpartInfo(letter=change['label'][-1],
                              title=change['title'],
                              urls=urls,
                              idx=change['child_labels'].index(label_id))
