

const Backbone = require('backbone');
const MetaModel = require('./meta-model');

Backbone.SidebarModel = MetaModel.extend({});

module.exports = new Backbone.SidebarModel({
  supplementalPath: 'sidebar',
});
