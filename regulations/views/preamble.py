from django.conf import settings
from django.http import Http404
from django.template.response import TemplateResponse
from django.views.generic.base import View

from regulations.generator.api_reader import ApiReader
from regulations.generator.generator import LayerCreator
from regulations.generator.html_builder import (
    CFRHTMLBuilder, PreambleHTMLBuilder)
from regulations.generator.layers.utils import is_contained_in
from regulations.views import utils
from regulations.views.diff import Versions, get_appliers


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
    layer_creator = LayerCreator()
    doc_id = '-'.join(subtree['label'])
    layer_creator.add_layers(utils.layer_names(request), 'preamble',
                             doc_id, sectional=True)
    builder = PreambleHTMLBuilder(
        *layer_creator.get_appliers(),
        id_prefix=id_prefix
    )
    builder.tree = subtree
    builder.generate_html()

    return {'node': builder.tree,
            'markup_page_type': 'reg-section'}


class PreambleView(View):
    """Displays either a notice preamble (or a subtree of that preamble). If
    using AJAX or specifically requesting, generate only the preamble markup;
    otherwise wrap it in the appropriate "chrome" """
    def get(self, request, *args, **kwargs):
        label_parts = kwargs.get('paragraphs', '').split('/')
        preamble = ApiReader().preamble(label_parts[0])
        if preamble is None:
            raise Http404

        subtree = find_subtree(preamble, label_parts)
        if subtree is None:
            raise Http404

        id_prefix = [str(label_parts[0]), 'preamble']
        context = generate_html_tree(subtree, request, id_prefix=id_prefix)

        context['use_comments'] = True
        context['section_prefix'] = '{}-preamble'.format(label_parts[0])
        template = context['node']['template_name']

        context = {
            'sub_context': context,
            'sub_template': template,
            'preamble': preamble,
            'section_prefix': '{}-preamble'.format(label_parts[0]),
            'doc_number': label_parts[0],
            'full_id': context['node']['full_id'],
        }
        if not request.is_ajax() and request.GET.get('partial') != 'true':
            template = 'regulations/preamble-chrome.html'
        else:
            template = 'regulations/preamble-partial.html'
        return TemplateResponse(request=request, template=template,
                                context=context)


class PrepareCommentView(View):
    def get(self, request, *args, **kwargs):
        preamble = ApiReader().preamble(kwargs['doc_number'])
        if preamble is None:
            raise Http404

        subtree = find_subtree(preamble, [kwargs['doc_number']])
        if subtree is None:
            raise Http404

        id_prefix = [kwargs['doc_number'], 'preamble']
        context = generate_html_tree(subtree, request, id_prefix=id_prefix)
        context.update({
            'preamble': preamble,
            'doc_number': kwargs['doc_number'],
        })
        template = 'regulations/comment-review-chrome.html'

        return TemplateResponse(request=request, template=template,
                                context=context)


class CFRChangesView(View):
    def get(self, request, doc_number, section):
        cfr_changes = getattr(settings, 'CFR_CHANGES', {})  # mock
        if doc_number not in cfr_changes:
            raise Http404("Doc # {} not found".format(doc_number))
        versions = cfr_changes[doc_number]["versions"]
        amendments = cfr_changes[doc_number]["amendments"]
        label_parts = section.split('-')

        if len(label_parts) == 1:
            context = self.authorities_context(amendments, cfr_part=section)
        else:
            context = self.regtext_changes_context(
                amendments,
                versions,
                doc_number=doc_number,
                label_id=section,
            )

        context['use_comments'] = True

        context = {
            'sub_context': context,
            'sub_template': 'regulations/cfr_changes.html',
            'preamble': None,
            'doc_number': doc_number,
            'full_id': '{}-cfr-{}'.format(doc_number, section),
        }

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

    @staticmethod
    def regtext_changes_context(amendments, version_info, label_id,
                                doc_number):
        """Generate diffs for the changed section"""
        cfr_part = label_id.split('-')[0]
        relevant = []
        for amd in amendments:
            keys = amd.get('changes', {}).keys()
            if any(is_contained_in(key, label_id) for key in keys):
                relevant.append(amd)

        versions = Versions(version_info[cfr_part]['left'],
                            version_info[cfr_part]['right'])
        tree = ApiReader().regulation(label_id, versions.older)
        appliers = get_appliers(label_id, versions)

        builder = CFRHTMLBuilder(*appliers, id_prefix=[str(doc_number), 'cfr'])
        builder.tree = tree
        builder.generate_html()
        return {'instructions': [a['instruction'] for a in relevant],
                'tree': builder.tree}
