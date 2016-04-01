'use strict';

var URI = require('urijs');
var _ = require('underscore');
var Backbone = require('backbone');
var MetaModel = require('./meta-model');

Backbone.PreambleModel = MetaModel.extend({
  getAJAXUrl: function(id) {
    // window.APP_PREFIX always ends in a slash
    var path = [window.APP_PREFIX + 'preamble'].concat(id.split('-'));
    return URI()
      .path(path.join('/'))
      .addQuery({partial: 'true'})
      .toString();
  }
});

module.exports = new Backbone.PreambleModel({});
