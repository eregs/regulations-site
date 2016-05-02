'use strict';
var URI = require('urijs');
var _ = require('underscore');
var Backbone = require('backbone');
var MetaModel = require('./meta-model');

Backbone.DiffModel = MetaModel.extend({});

var diffModel = new Backbone.DiffModel({
  getAJAXUrl: function(id, options) {
    return window.APP_PREFIX + 'partial/diff/' + this.assembleDiffURL(options);
  },

  // ex: diff/1005-1/2011-12121/2012-11111/?from_version=2012-11111
  assembleDiffURL: function(options) {
    return URI([options.id, options.baseVersion, options.newerVersion].join('/'))
      .query({from_version: options.fromVersion})
      .toString();
  }
});

module.exports = diffModel;
