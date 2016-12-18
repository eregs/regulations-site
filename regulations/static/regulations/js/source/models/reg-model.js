

const Backbone = require('backbone');
const MetaModel = require('./meta-model');

Backbone.RegModel = MetaModel.extend({});

module.exports = new Backbone.RegModel();
