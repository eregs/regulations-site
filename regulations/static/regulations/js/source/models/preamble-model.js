'use strict';

var URI = require('urijs');
var _ = require('underscore');
var Backbone = require('backbone');
var MetaModel = require('./meta-model');
var helpers = require('../helpers');

Backbone.PreambleModel = MetaModel.extend({
  getAJAXUrl: function(id) {
    var path = helpers.parsePreambleId(id).path;
    path[0] = window.APP_PREFIX + path[0];
    return URI()
      .path(path.join('/'))
      .addQuery({partial: 'true'})
      .toString();
  },
});

module.exports = new Backbone.PreambleModel({});
