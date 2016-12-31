

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');

Backbone.$ = $;

const DrawerEvents = _.clone(Backbone.Events);
module.exports = DrawerEvents;
