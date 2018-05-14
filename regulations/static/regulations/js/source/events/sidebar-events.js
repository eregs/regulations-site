

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');

Backbone.$ = $;

const SidebarEvents = _.clone(Backbone.Events);
module.exports = SidebarEvents;
