'use strict';

var $ = require('jquery');
var Backbone = require('backbone');

var comment_model = Backbone.Model.extend({
  defaults: {
    docId: '',
    label: '',
    comment: '',
    commentHtml: '',
    files: []
  }
});

var comment_comparator = function(first, second) {
    if (first.get('tocId') < second.get('tocId')) {
        return -1;
    } else if (first.get('tocId') > second.get('tocId')) {
        return 1;
    } else if (first.get('indexes') < second.get('indexes')) {
        return -1;
    } else if (first.get('indexes') > second.get('indexes')) {
        return 1;
    } else {
        return 0;
    }
};

module.exports = {
    CommentModel: comment_model,
    commentComparator: comment_comparator
};
