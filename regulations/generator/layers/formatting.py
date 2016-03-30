from django.template import loader, Context

from regulations.generator.layers.base import SearchReplaceLayer


class FormattingLayer(SearchReplaceLayer):
    shorthand = 'formatting'
    data_source = 'formatting'
    DATA_TYPES = ('table', 'fence', 'subscript', 'dash', 'footnote',
                  'superscript')

    def __init__(self, layer):
        self.layer = layer
        self.tpls = {
            key: loader.get_template('regulations/layers/{}.html'.format(key))
            for key in ('table', 'note', 'code', 'subscript', 'dash',
                        'footnote', 'superscript')}

    def render_table(self, table, data_type=None):
        max_width = 0
        for header_row in table['header']:
            width = sum(cell['colspan'] for cell in header_row)
            max_width = max(max_width, width)

        #  Just in case a row is longer than the header
        row_max = max(len(row) for row in table['rows'])
        max_width = max(max_width, row_max)

        #  Now pad rows if needed
        for row in table['rows']:
            row.extend([''] * (max_width - len(row)))

        context = Context(table)
        #   Remove new lines so that they don't get escaped on display
        return self.tpls['table'].render(context).replace('\n', '')

    def render_fence(self, fence, data_type=None):
        """Fenced paragraphs are formatted separately, offset from the rest of
        the text. They have an associated "type" which further specifies their
        format"""
        _type = fence.get('type')
        lines = fence.get('lines', [])
        strip_nl = True
        if _type == 'note':
            lines = [l.replace('Note:', '').replace('Notes:', '')
                     for l in lines]
            lines = [l for l in lines if l.strip()]
            tpl = self.tpls['note']
        else:   # Generic "code"/ preformatted
            strip_nl = False
            tpl = self.tpls['code']

        rendered = tpl.render(Context({'lines': lines, 'type': _type}))
        if strip_nl:
            rendered = rendered.replace('\n', '')
        return rendered

    def render_replacement(self, data, data_type):
        """Several of the formatted data types are simple string replacements.
        Implement them all here"""
        context = Context(data)
        return self.tpls[data_type].render(context).replace('\n', '')

    def replacements_for(self, original, data):
        for data_type in self.DATA_TYPES:
            processor = getattr(self, 'render_' + data_type,
                                self.render_replacement)
            key = data_type + '_data'
            if key in data:
                yield processor(data[key], data_type)
