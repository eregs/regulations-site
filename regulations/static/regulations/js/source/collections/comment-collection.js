

const _ = require('underscore');
const Backbone = require('backbone');
Backbone.LocalStorage = require('backbone.localstorage');

const commentModel = require('../models/comment-model');

const CommentCollection = Backbone.Collection.extend({
  model: commentModel.CommentModel,
  localStorage: new Backbone.LocalStorage('eregsnc'),

  filter: function filter(docId) {
    return _.filter(this.models, model => model.get('docId') === docId);
  },

  toJSON: function toJSON(options) {
    const models = (options || {}).docId ? this.filter(options.docId) : this.models;
    return _.map(models, model => model.toJSON(options));
  },

  comparator: commentModel.commentComparator,
});

const comments = new CommentCollection();
comments.fetch();

module.exports = comments;
