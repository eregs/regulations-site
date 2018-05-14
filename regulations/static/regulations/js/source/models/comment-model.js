

const Backbone = require('backbone');

const commentModel = Backbone.Model.extend({
  defaults: {
    docId: '',
    label: '',
    comment: '',
    commentHtml: '',
    files: [],
    indexes: [],
  },
});

const indexComparator = function indexComparator(first, second) {
  const maxLength = Math.max(first.length, second.length);

  for (let i = 0; i < maxLength; i += 1) {
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

const commentComparator = function commentComparator(first, second) {
  return indexComparator(first.get('indexes'), second.get('indexes'));
};

module.exports = {
  CommentModel: commentModel,
  commentComparator,
};
