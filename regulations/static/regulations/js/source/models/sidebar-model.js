'use strict';

var Backbone = require('backbone');
var MetaModel = require('./meta-model');

Backbone.SidebarModel = MetaModel.extend({});

module.exports = new Backbone.SidebarModel({
  supplementalPath: 'sidebar',
});
