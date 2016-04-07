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

var CACHE_KEY = 'eregs:key';

// Cache comment models to S3 on sync
// TODO: Fetch and rehydrate models on load
comments.on('sync', function() {
  var data = JSON.stringify(comments.toJSON({}));
  $.ajax({
    type: 'GET',
    url: window.APP_PREFIX + 'comments/cache',
    data: {
      key: window.localStorage.getItem(CACHE_KEY),
      size: unescape(encodeURI(data)).length  // Length of encoded string
    }
  }).then(function(resp) {
    window.localStorage.setItem(CACHE_KEY, resp.key);
    return $.ajax({
      type: 'PUT',
      url: resp.url,
      data: data,
      contentType: 'application/json',
      processData: false
    });
  }).fail(function() {
    console.log('Comment cache failed');
  });
});

module.exports = comments;
