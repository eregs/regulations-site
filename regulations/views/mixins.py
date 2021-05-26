from django.urls import NoReverseMatch


def build_citation(context):
    citation = []
    if 'part' in context:
        citation.append(context["part"])
        if 'section' in context:
            citation.append(context["section"])
        elif 'subpart' in context:
            citation.append(context["subpart"])
    return citation


class CitationContextMixin:
    def get_context_data(self, **kwargs):
        context = super(CitationContextMixin, self).get_context_data(**kwargs)
        context['citation'] = build_citation(context)
        return context


class TableOfContentsMixin:
    def build_toc_urls(self, context, toc, node=None):
        if node is None:
            node = toc

        if any(node['type'] == x for x in ['subpart', 'section', 'subject_group']):
            try:
                identifier = '-'.join(node['identifier'])
                node['url'] = self.build_toc_url(context, toc, node) + "#" + identifier
            except NoReverseMatch:
                pass
        if node['children'] is not None:
            for child in node['children']:
                self.build_toc_urls(context, toc, child)

    def build_toc_url(self, context, toc, node):
        raise NotImplementedError()
