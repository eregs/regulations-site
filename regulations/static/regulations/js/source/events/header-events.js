

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');

Backbone.$ = $;

const HeaderEvents = _.clone(Backbone.Events);
module.exports = HeaderEvents;
