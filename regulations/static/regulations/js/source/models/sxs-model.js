

const Backbone = require('backbone');
const MetaModel = require('./meta-model');

Backbone.SxSModel = MetaModel.extend({});

const sxsModel = new Backbone.SxSModel({
  supplementalPath: 'sxs',
});

module.exports = sxsModel;
