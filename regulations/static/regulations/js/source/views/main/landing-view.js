'use strict';
var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
var Router = require('../../router');
var MainEvents = require('../../events/main-events');
Backbone.$ = $;

var LandingView = Backbone.View.extend({
    
    el: '#content-body',
    landingContentKey: 'landing-content',

    initialize: function() {
        console.log('Fraggle ' + Backbone.history.fragment);
        this.setContent();
        this.externalEvents = MainEvents;
        this.externalEvents.on('landing:open', this.render);
        this.externalEvents.on('landing:set', this.setContent);
    },

    setContent: function() {
        console.log('Fraggle ' + Backbone.history.fragment);
        // Backbone history check here is invalid - would remove that
        // check once the router "landing:set" event was working
        if (typeof(Storage) !== "undefined" && 
            Backbone.history.fragment.indexOf("/") == -1) {
            console.log('setting content');
            localStorage.setItem(this.landingContentKey, $('#content-body').html());
        }
    },

    render: function() {
        if (typeof(Storage) !== "undefined" && 
            localstorage.getItem(this.landingContentKey)) {
                // for some reason this.$el is not working
                $('#content-body').html(localStorage.getItem(this.landingContentKey));
        }
    }
});

module.exports = LandingView;