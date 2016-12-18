

const URI = require('urijs');
const Backbone = require('backbone');
const MetaModel = require('./meta-model');
const helpers = require('../helpers');

Backbone.PreambleModel = MetaModel.extend({
  getAJAXUrl: function getAJAXUrl(id) {
    const path = helpers.parsePreambleId(id).path;
    path[0] = window.APP_PREFIX + path[0];
    return URI()
      .path(path.join('/'))
      .addQuery({ partial: 'true' })
      .toString();
  },
});

module.exports = new Backbone.PreambleModel({});
