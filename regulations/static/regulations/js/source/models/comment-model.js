'use strict';

var $ = require('jquery');
var Backbone = require('backbone');

var commentModel = Backbone.Model.extend({
  defaults: {
    docId: '',
    label: '',
    comment: '',
    commentHtml: '',
    files: [],
    indexes: [],
  },
});

var indexComparator = function indexComparator(first, second) {
  var maxLength = Math.max(first.length, second.length);

  for (var i = 0; i < maxLength; i += 1) {
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

var commentComparator = function commentComparator(first, second) {
  return indexComparator(first.get('indexes'), second.get('indexes'));
};

module.exports = {
  CommentModel: commentModel,
  commentComparator: commentComparator,
};
