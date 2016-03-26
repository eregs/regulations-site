'use strict';

var $ = require('jquery');
var Backbone = require('backbone');
Backbone.LocalStorage = require('backbone.localstorage');

var CommentModel = require('../models/comment-model');

var CommentCollection = Backbone.Collection.extend({
  model: CommentModel,
  localStorage: new Backbone.LocalStorage('comment:' + window.DOC_NUMBER)
});

var comments = new CommentCollection();
comments.fetch();

module.exports = comments;
