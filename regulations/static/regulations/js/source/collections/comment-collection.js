'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.LocalStorage = require('backbone.localstorage');

var CommentModel = require('../models/comment-model');

var CommentCollection = Backbone.Collection.extend({
  model: CommentModel,
  localStorage: new Backbone.LocalStorage('eregsnc'),

  filter: function(docId) {
    return _.filter(this.models, function(model) {
      return model.get('docId') === docId;
    });
  },

  toJSON: function(options) {
    var models = (options || {}).docId ? this.filter(options.docId) : this.models;
    return _.map(models, function(model) {
      return model.toJSON(options);
    });
  }
});

var comments = new CommentCollection();
comments.fetch();

module.exports = comments;
