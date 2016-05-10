'use strict';

var $ = require('jquery');
var Backbone = require('backbone');

var comment_model = Backbone.Model.extend({
  defaults: {
    docId: '',
    tocId: '',
    label: '',
    comment: '',
    commentHtml: '',
    files: [],
    preorder: []
  }
});

var int_array_comparator = function(first, second) {
    var max_length = Math.max(first.length, second.length)

    for (var i = 0; i < max_length; i++) {
        if (first[i] === undefined) {
            return -1;
        } else if (second[i] === undefined) {
            return 1;
        } else if (first[i] < second[i]) {
            return -1;
        } else if (first[i] > second[i]) {
            return 1;
        }
    }
    return 0;
};

var comment_comparator = function(first, second) {
    /* The preamble comes before the CFR changes.
     * Within the preamble or CFR part, sorting is by preorder.
     */
    var first_part = first.get('tocId').split('-')[1]
    var second_part = second.get('tocId').split('-')[1]
    if (first_part == second_part) {
        return int_array_comparator(first.get('preorder'), second.get('preorder'));
    } else if (first_part == 'preamble') {
        return -1;
    } else {
        return 1;
    }
};

module.exports = {
    CommentModel: comment_model,
    commentComparator: comment_comparator
};
