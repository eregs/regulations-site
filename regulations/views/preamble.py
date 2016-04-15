from collections import namedtuple
from datetime import date

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404
from django.template.response import TemplateResponse
from django.views.generic.base import View

from regulations.generator.api_reader import ApiReader
from regulations.generator.generator import LayerCreator
from regulations.generator.html_builder import (
    CFRChangeHTMLBuilder, PreambleHTMLBuilder)
from regulations.generator.layers.utils import (
    convert_to_python, is_contained_in)
from regulations.generator.toc import fetch_toc
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


ToCPart = namedtuple('ToCPart', ['title', 'part', 'name', 'authority_url',
                                 'sections'])
ToCSect = namedtuple('ToCSect', ['section', 'url', 'title', 'full_id'])


class CFRChangeToC(object):
    """Builds the ToC specific to CFR changes from amendment data. As there is
    some valuable state shared between amendment processing, we store it all
    in an object"""
    def __init__(self, doc_number, version_info):
        """version_info structure: {cfr_part -> {"left": str, "right": str}}
        e.g.  {"111": {"left": "v1", "right": "v2"},
               "222": {"left": "vold", "right": "vnew"}}"""
        self.current_part = None
        self.current_section = None
        self.section_titles = {}
        self.toc = []
        self.doc_number = doc_number
        self.version_info = version_info

    def add_amendment(self, amendment):
        """Process a single amendment, of the form
        {'cfr_part': 111, 'instruction': 'text1', 'authority': 'text2'} or
        {'cfr_part': 111, 'instruction': 'text3',
         'changes': [['111-22-c', [data1]], ['other', [data2]]}"""
        if (self.current_part is None or
                self.current_part.part != amendment['cfr_part']):
            self.new_cfr_part(amendment)

        changes = amendment.get('changes', [])
        if isinstance(changes, dict):
            changes = changes.items()
        for change_label, _ in changes:
            self.add_change(change_label.split('-'))

    def new_cfr_part(self, amendment):
        """While processing an amendment, if it refers to a CFR part which
        hasn't been seen before, we need to perform some accounting, fetching
        related meta data, etc."""
        part = amendment['cfr_part']
        meta = utils.regulation_meta(part, self.version_info[part]['right'])
        flat_toc = fetch_toc(part, self.version_info[part]['right'],
                             flatten=True)
        self.section_titles = {elt['index'][1]: elt['title']
                               for elt in flat_toc if len(elt['index']) == 2}
        self.current_part = ToCPart(
            title=meta.get('cfr_title_number'), part=part,
            name=meta.get('statutory_name'), sections=[],
            authority_url=reverse('cfr_changes', kwargs={
                'doc_number': self.doc_number, 'section': part}))
        self.current_section = None
        self.toc.append(self.current_part)

    def add_change(self, label_parts):
        """While processing an amendment, we will encounter sections we
        haven't seen before -- these will ultimately be ToC entries"""
        change_section = label_parts[1]
        if (self.current_section is None or
                self.current_section.section != change_section):

            section = '-'.join(label_parts[:2])
            self.current_section = ToCSect(
                section=change_section,
                title=self.section_titles.get(change_section),
                full_id='{}-cfr-{}'.format(self.doc_number, section),
                url=reverse('cfr_changes', kwargs={
                    'doc_number': self.doc_number,
                    'section': section}))
            self.current_part.sections.append(self.current_section)

    @classmethod
    def for_doc_number(cls, doc_number):
        """Soup to nuts conversion from a document number to a table of
        contents list"""
        cfr_changes = getattr(settings, 'CFR_CHANGES', {})  # mock
        if doc_number not in cfr_changes:
            raise Http404("Doc # {} not found".format(doc_number))
        cfr_changes = cfr_changes[doc_number]
        builder = cls(doc_number, cfr_changes['versions'])
        for amendment in cfr_changes['amendments']:
            builder.add_amendment(amendment)
        return builder.toc


PreambleSect = namedtuple(
    'PreambleSect',
    ['depth', 'full_id', 'title', 'url', 'children'],
)


def make_preamble_toc(nodes, depth=1, max_depth=3):
    intro_subheader = depth == 2 and any('intro' in n['label'] for n in nodes)
    if depth > max_depth or intro_subheader:
        return []
    return [
        PreambleSect(
            depth=depth,
            title=node['title'],
            url='{}#{}'.format(
                reverse(
                    'chrome_preamble',
                    kwargs={'paragraphs': '/'.join(node['label'][:2])},
                ),
                '-'.join(node['label']),
            ),
            full_id='{}-preamble-{}'.format(
                node['label'][0],
                '-'.join(node['label']),
            ),
            children=make_preamble_toc(
                node.get('children', []),
                depth=depth + 1,
                max_depth=max_depth,
            )
        )
        for node in nodes
        if node.get('title')
    ]


class PreambleView(View):
    """Displays either a notice preamble (or a subtree of that preamble). If
    using AJAX or specifically requesting, generate only the preamble markup;
    otherwise wrap it in the appropriate "chrome" """
    def get(self, request, *args, **kwargs):
        label_parts = kwargs.get('paragraphs', '').split('/')
        doc_number = label_parts[0]
        preamble = ApiReader().preamble(doc_number)
        if preamble is None:
            raise Http404

        # @todo - right now we're shimming in fake data; eventually this data
        # should come from the API
        intro = getattr(settings, 'PREAMBLE_INTRO', {}).get(doc_number, {})
        if intro.get('tree'):
            preamble['children'].insert(0, intro['tree'])
        intro['meta'] = convert_to_python(intro.get('meta', {}))
        if 'comments_close' in intro['meta']:
            intro['meta']['days_remaining'] = 1 + (
                intro['meta']['comments_close'].date() - date.today()).days

        subtree = find_subtree(preamble, label_parts)
        if subtree is None:
            raise Http404

        id_prefix = [doc_number, 'preamble']
        context = generate_html_tree(subtree, request, id_prefix=id_prefix)
        context['meta'] = intro['meta']

        template = context['node']['template_name']

        context = {
            'sub_context': context,
            'sub_template': template,
            'doc_number': doc_number,
            'full_id': context['node']['full_id'],
            'preamble_toc': make_preamble_toc(preamble['children']),
            'cfr_change_toc': CFRChangeToC.for_doc_number(doc_number)
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


# @todo - this shares a lot of code w/ PreambleView. Can we merge them?
class CFRChangesView(View):
    def get(self, request, doc_number, section):
        cfr_changes = getattr(settings, 'CFR_CHANGES', {})  # mock
        if doc_number not in cfr_changes:
            raise Http404("Doc # {} not found".format(doc_number))
        preamble = ApiReader().preamble(doc_number)
        if preamble is None:
            raise Http404
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

        context = {
            'sub_context': context,
            'sub_template': 'regulations/cfr_changes.html',
            'preamble': preamble,
            'doc_number': doc_number,
            'full_id': '{}-cfr-{}'.format(doc_number, section),
            'preamble_toc': make_preamble_toc(preamble['children']),
            'cfr_change_toc': CFRChangeToC.for_doc_number(doc_number)
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
            changes = amd.get('changes', [])
            if isinstance(changes, dict):
                changes = list(changes.items())
            keys = {change[0] for change in changes}
            if any(is_contained_in(key, label_id) for key in keys):
                relevant.append(amd)

        versions = Versions(version_info[cfr_part]['left'],
                            version_info[cfr_part]['right'])
        tree = ApiReader().regulation(label_id, versions.older)
        appliers = get_appliers(label_id, versions)

        builder = CFRChangeHTMLBuilder(
            *appliers, id_prefix=[str(doc_number), 'cfr'])
        builder.tree = tree
        builder.generate_html()
        return {'instructions': [a['instruction'] for a in relevant],
                'tree': builder.tree}
