

const Backbone = require('backbone');
const MetaModel = require('./meta-model');

Backbone.DefinitionModel = MetaModel.extend({});

const definitionModel = new Backbone.DefinitionModel({
  supplementalPath: 'definition',
});

module.exports = definitionModel;
