'use strict';

var URI = require('urijs');
var _ = require('underscore');
var Backbone = require('backbone');
var MetaModel = require('./meta-model');

Backbone.PreambleModel = MetaModel.extend({
  getAJAXUrl: function(id) {
    var path = ['preamble'].concat(id.split('-'));
    if (window.APP_PREFIX) {
      path = [window.APP_PREFIX].concat(path);
    }
    return URI()
      .path(path.join('/'))
      .addQuery({'partial': 'true'})
      .toString();
  }
});

module.exports = new Backbone.PreambleModel({});
