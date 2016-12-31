

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');

Backbone.$ = $;

const GAEvents = _.clone(Backbone.Events);
module.exports = GAEvents;
