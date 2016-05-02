'use strict';
var URI = require('urijs');
var _ = require('underscore');
var Backbone = require('backbone');
var MetaModel = require('./meta-model');

Backbone.SearchModel = MetaModel.extend({});

var searchModel = new Backbone.SearchModel({
    supplementalPath: 'search',

    getAJAXUrl: function(id, options) {
      var url = window.APP_PREFIX + 'partial/';

      if (typeof this.supplementalPath !== 'undefined') {
        url += this.supplementalPath + '/';
      }

      return url + this.assembleSearchURL(options);
    },

    assembleSearchURL: function(options) {
      var docType = options.docType || 'cfr';
      var path = [docType, options.docId].join('/');
      var query = {q: options.query};
      if (options.regVersion) {
        query.version = options.regVersion;
      }
      if (typeof options.page !== 'undefined') {
        query.page = options.page;
      }
      return URI(path).query(query).toString();
    }
});

module.exports = searchModel;
