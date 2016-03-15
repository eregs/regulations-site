'use strict';
var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
var Router = require('../../router');
var HeaderEvents = require('../../events/header-events');
var DrawerEvents = require('../../events/drawer-events');
var Helpers = require('../../helpers');
var Resources = require('../../resources');
var MainEvents = require('../../events/main-events');
var ChildView = require('./child-view');
Backbone.$ = $;

var PreambleView = ChildView.extend({
    el: '#preamble-content',

    // preamble and comment related functions

    initialize: function() {


    }

});

// module.exports = PreambleView;
var preamble_view = new PreambleView();
