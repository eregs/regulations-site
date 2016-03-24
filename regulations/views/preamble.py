from django.http import Http404
from django.template.response import TemplateResponse
from django.views.generic.base import View

from regulations.generator.api_reader import ApiReader
from regulations.generator.generator import LayerCreator
from regulations.generator.html_builder import HTMLBuilder
from regulations.views import utils


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


def generate_html_tree(subtree, request):
    """Use the HTMLBuilder to generate a version of this subtree with
    appropriate markup. Currently, includes no layers"""
    layer_creator = LayerCreator()
    doc_id = '-'.join(subtree['label'])
    layer_creator.add_layers(utils.layer_names(request), 'preamble',
                             doc_id, sectional=True)
    builder = HTMLBuilder(*layer_creator.get_appliers())
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

        context = generate_html_tree(subtree, request)
        context['use_comments'] = True
        template = context['node']['template_name']

        context = {'sub_context': context, 'sub_template': template,
                   'preamble': preamble, 'doc_number': label_parts[0]}
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

        context = generate_html_tree(subtree, request)
        context.update({
            'preamble': preamble,
            'doc_number': kwargs['doc_number'],
        })
        template = 'regulations/comment-review-chrome.html'

        return TemplateResponse(request=request, template=template,
                                context=context)
