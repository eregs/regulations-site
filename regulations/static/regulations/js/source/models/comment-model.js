'use strict';

var $ = require('jquery');
var Backbone = require('backbone');

module.exports = Backbone.Model.extend({
  defaults: {
    docId: '',
    label: '',
    comment: '',
    commentHtml: '',
    files: []
  }
});
