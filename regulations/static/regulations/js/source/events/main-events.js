

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');

Backbone.$ = $;

const MainEvents = _.clone(Backbone.Events);
module.exports = MainEvents;
