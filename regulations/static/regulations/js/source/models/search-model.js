

const URI = require('urijs');
const Backbone = require('backbone');
const MetaModel = require('./meta-model');

Backbone.SearchModel = MetaModel.extend({});

const searchModel = new Backbone.SearchModel({
  supplementalPath: 'search',

  getAJAXUrl: function getAJAXUrl(id, options) {
    let url = `${window.APP_PREFIX}partial/`;

    if (typeof this.supplementalPath !== 'undefined') {
      url += `${this.supplementalPath}/`;
    }

    return url + this.assembleSearchURL(options);
  },

  assembleSearchURL: function assembleSearchURL(options) {
    const docType = options.docType || 'cfr';
    const path = [docType, options.docId].join('/');
    const query = { q: options.query };
    if (options.regVersion) {
      query.version = options.regVersion;
    }
    if (typeof options.page !== 'undefined') {
      query.page = options.page;
    }
    return URI(path).query(query).toString();
  },
});

module.exports = searchModel;
