'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');

Backbone.$ = $;

module.exports = _.clone(Backbone.Events);
