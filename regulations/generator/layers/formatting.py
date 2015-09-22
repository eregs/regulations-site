from django.template import loader, Context


class FormattingLayer(object):
    shorthand = 'formatting'

    def __init__(self, layer_data):
        self.layer_data = layer_data
        self.table_tpl = loader.get_template('regulations/layers/table.html')
        self.note_tpl = loader.get_template('regulations/layers/note.html')
        self.extract_tpl = loader.get_template(
            'regulations/layers/extract.html')
        self.code_tpl = loader.get_template('regulations/layers/code.html')
        self.subscript_tpl = loader.get_template(
            'regulations/layers/subscript.html')
        self.dash_tpl = loader.get_template('regulations/layers/dash.html')

    def render_table(self, table):
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
        return self.table_tpl.render(context).replace('\n', '')

    def render_fence(self, fence):
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
            tpl = self.note_tpl
        elif _type == 'extract':
            lines = [l for l in lines if l.strip()]
            tpl = self.extract_tpl
        else:   # Generic "code"/ preformatted
            strip_nl = False
            tpl = self.code_tpl

        rendered = tpl.render(Context({'lines': lines, 'type': _type}))
        if strip_nl:
            rendered = rendered.replace('\n', '')
        return rendered

    def render_subscript(self, subscript):
        context = Context(subscript)
        return self.subscript_tpl.render(context).replace('\n', '')

    def render_dash(self, dash):
        context = Context(dash)
        return self.dash_tpl.render(context).replace('\n', '')

    def apply_layer(self, text_index):
        """Convert all plaintext tables into html tables"""
        layer_pairs = []
        data_types = ['table', 'fence', 'subscript', 'dash']
        for data in self.layer_data.get(text_index, []):
            for data_type in data_types:
                processor = getattr(self, 'render_' + data_type)
                key = data_type + '_data'
                if key in data:
                    layer_pairs.append((data['text'],
                                        processor(data[key]),
                                        data['locations']))
        return layer_pairs
