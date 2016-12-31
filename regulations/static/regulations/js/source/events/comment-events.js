

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');

Backbone.$ = $;

module.exports = _.clone(Backbone.Events);
