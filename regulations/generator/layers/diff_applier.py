import copy
from collections import Counter, deque, namedtuple

from regulations.generator.layers import tree_builder


class DiffApplier(object):
    """ Diffs between two versions of a regulation are represented in our
    particular JSON format. This class applies that diff to the older version
    of the regulation, generating HTML that clearly shows the changes between
    old and new. """

    INSERT = u'insert'
    DELETE = u'delete'
    EQUAL = u'equal'

    DELETED_OP = 'deleted'
    ADDED_OP = 'added'
    MODIFIED_OP = 'modified'

    def __init__(self, diff_json, label_requested):
        self.diff = diff_json
        # label_requested is the regulation label for which a diff is
        # requested.
        self.label_requested = label_requested

    def deconstruct_text(self, original):
        self.oq = [deque([c]) for c in original]

    def insert_text(self, pos, new_text):
        if pos == len(self.oq):
            self.oq[pos-1].extend(['<ins>', new_text, '</ins>'])
        else:
            self.oq[pos].appendleft('<ins>' + new_text + '</ins>')

    def delete_text(self, start, end):
        self.oq[start].appendleft('<del>')
        self.oq[end-1].append('</del>')

    def get_text(self):
        return ''.join([''.join(d) for d in self.oq])

    def delete_all(self, text):
        """ Mark all the text passed in as deleted. """
        return '<del>' + text + '</del>'

    def add_all(self, text):
        """ Mark all the text passed in as deleted. """
        return '<ins>' + text + '</ins>'

    _LabelOp = namedtuple('LabelOp', ['label', 'op'])

    def set_child_labels(self, node):
        """As we display removed, added, and unchanged nodes, the children of
        a node will contain all three types. Pull the 'child_ops' data to
        derive the correct order of these combined children"""
        instructs = self.diff.get('-'.join(node['label']), {})
        if 'child_labels' not in instructs and 'child_ops' in instructs:
            original_labels = ['-'.join(c['label']) for c in node['children']]
            label_ops = []
            for op, start, end_or_labels in instructs['child_ops']:
                if isinstance(end_or_labels, list):
                    labels = end_or_labels
                else:
                    labels = original_labels[start:end_or_labels]
                label_ops.extend(DiffApplier._LabelOp(l, op) for l in labels)
            label_ops = self.remove_moved_labels(label_ops)
            node['child_labels'] = [lo.label for lo in label_ops]

    @classmethod
    def has_moved(cls, label_op, seen_count):
        """A label is moved if it's been deleted in one position but added int
        another"""
        if seen_count[label_op.label] == 1:
            return False
        else:   # We want to keep the final destination (INSERT)
            return label_op.op != cls.INSERT

    def remove_moved_labels(self, label_ops):
        """If a label has been moved, we will display it in the new position"""
        seen_count = Counter(label_op.label for label_op in label_ops)

        return [lo for lo in label_ops if not self.has_moved(lo, seen_count)]

    def add_nodes_to_tree(self, original, adds):
        """ Add all the nodes from new_nodes into the original tree. """
        tree_hash = tree_builder.build_tree_hash(original)
        for node in tree_hash.values():
            self.set_child_labels(node)

        for label, node in adds.queue:
            p_label = '-'.join(tree_builder.parent_label(node))
            if tree_builder.parent_in_tree(p_label, tree_hash):
                tree_builder.add_node_to_tree(node, p_label, tree_hash)
                adds.delete(label)
            else:
                parent = adds.find(p_label)
                if parent:
                    tree_builder.add_child(parent[1], node)
                else:
                    original.update(node)

    def is_child_of_requested(self, label):
        """ Return true if the label is a child of the requested label.  """
        req = self.label_requested
        if 'Interp' in label and 'Interp' in req:
            # Sub-paragraph
            if label.startswith(req + '-'):
                return True
            # The parent must not be a sub paragraph if the prefixes differ
            if not req.endswith('-Interp'):
                return False
            req_interpreting = req[:req.find('-Interp')]
            child_interpreting = label[:label.find('-Interp')]
            return child_interpreting.startswith(req_interpreting + '-')
        elif 'Interp' not in label and 'Interp' not in req:
            return label.startswith(req + '-')
        return False

    def relevant_added(self, label):
        """ Get the operations that add nodes, for the requested
        section/pargraph. """

        if (self.diff[label]['op'] == self.ADDED_OP
            and (label == self.label_requested
                 or self.is_child_of_requested(label))):
            return True

    def tree_changes(self, original_tree):
        """ Apply additions to the regulation tree. """

        def node(diff_node, label):
            """ Take diff's specification of a node, and actually turn it into
            a regulation node. """

            node = copy.deepcopy(diff_node)
            node['children'] = []
            if 'title' in node and node['title'] is None:
                del node['title']
            return node

        new_nodes = [(label, node(self.diff[label]['node'], label))
                     for label in self.diff if self.relevant_added(label)]

        adds = tree_builder.AddQueue()
        adds.insert_all(new_nodes)

        self.add_nodes_to_tree(original_tree, adds)

    def apply_diff_changes(self, original, diff_list):
        """Account for modified text"""
        self.deconstruct_text(original)
        for d in diff_list:
            if d[0] == self.INSERT:
                _, pos, new_text = d
                self.insert_text(pos, new_text)
            if d[0] == self.DELETE:
                _, s, e = d
                self.delete_text(s, e)
            if isinstance(d[0], list):
                if d[0][0] == self.DELETE and d[1][0] == self.INSERT:
                    # Text replace scenario.
                    _, s, e = d[0]
                    self.delete_text(s, e)

                    _, _, new_text = d[1]

                    # Place the new text at the end of the delete for
                    # readability.
                    self.insert_text(e, new_text)
        return self.get_text()

    def apply_diff(self, original, label, component='text'):
        """Here we delete or add whole nodes in addition to passing to
        `apply_diff_changes` when text has been modified"""
        if label in self.diff:
            if self.diff[label]['op'] == self.DELETED_OP:
                return self.delete_all(original)
            if self.diff[label]['op'] == self.ADDED_OP:
                return self.add_all(original)
            if component in self.diff[label]:
                text_diffs = self.diff[label][component]
                return self.apply_diff_changes(original, text_diffs)
        return original
