

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');

Backbone.$ = $;

const BreakawayEvents = _.clone(Backbone.Events);
module.exports = BreakawayEvents;
