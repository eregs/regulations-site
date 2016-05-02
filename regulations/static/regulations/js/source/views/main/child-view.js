'use strict';
var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
require('../../events/scroll-stop.js');
var Router = require('../../router');
var HeaderEvents = require('../../events/header-events');
var DrawerEvents = require('../../events/drawer-events');
var Helpers = require('../../helpers');
var MainEvents = require('../../events/main-events');
var GAEvents = require('../../events/ga-events');
Backbone.$ = $;

var ChildView = Backbone.View.extend({
    el: '#content-wrapper',

    initialize: function(options) {
        this.options = options;

        this.attachWayfinding();

        if (this.options.render) {
          if (!this.title) {
            this.title = this.assembleTitle();
          }
          this.route(this.options);
          GAEvents.trigger('section:open', this.options);
          this.render();
        } else if (this.options.id) {
          MainEvents.trigger('section:sethandlers');
          DrawerEvents.trigger('section:open', this.options.id);
        }

        this.$sections = this.$sections || {};
        this.activeSection = this.options.id;
        this.$activeSection = $('#' + this.activeSection);

        this.loadImages();
    },

    attachWayfinding: function() {
        this.updateWayfinding();
        // * when a scroll event completes, check what the active secion is
        // we can't scope the scroll to this.$el because there's no localized
        // way to grab the scroll event, even with overflow:scroll
        $(window).on('scrollstop', (_.bind(this.checkActiveSection, this)));
    },

    render: function() {
        this.updateWayfinding();
        this.loadImages();
        this.scroll();
        HeaderEvents.trigger('section:open', this.id);
        DrawerEvents.trigger('section:open', this.id);
    },

    scroll: function() {
      var offsetTop, $scrollToId;
      if (this.options.scrollToId) {
        $scrollToId = $('#' + this.options.scrollToId);
        if ($scrollToId.length) {
          offsetTop = $scrollToId.offset().top;
        }
        window.scrollTo(0, offsetTop || 0);
      }
    },

    changeFocus: function(id) {
        $(id).focus();
    },

    assembleTitle: function() {
        var titleParts, newTitle;
        titleParts = _.compact(document.title.split(' '));
        newTitle = [titleParts[0], titleParts[1], Helpers.idToRef(this.id), '|', 'eRegulations'];
        return newTitle.join(' ');
    },

    // naive way to update the active table of contents link and wayfinding header
    // once a scroll event ends, we loop through each content section DOM node
    // the first one whose offset is greater than the window scroll position, accounting
    // for the fixed position header, is deemed the active section
    checkActiveSection: function() {
        var len = this.$contentContainer.length - 1;

        for (var i = 0; i <= len; i++) {
            if (this.$sections[i].offset().top + this.$contentHeader.height() >= $(window).scrollTop()) {
                if (_.isEmpty(this.activeSection) || (this.activeSection !== this.$sections[i].id)) {
                    this.activeSection = this.$sections[i][0].id;
                    this.$activeSection = $(this.$sections[i][0]);
                    // **Event** trigger active section change
                    HeaderEvents.trigger('section:open', this.activeSection);
                    DrawerEvents.trigger('section:open', this.$activeSection.data('toc-id') || this.id);
                    MainEvents.trigger('paragraph:active', this.activeSection);

                    if (typeof window.history !== 'undefined' && typeof window.history.replaceState !== 'undefined') {
                        // update hash in url
                        window.history.replaceState(
                            null,
                            null,
                            window.location.origin + window.location.pathname + window.location.search + '#' + this.activeSection
                        );
                    }

                    return;
                }
            }
        }

        return this;
    },

    updateWayfinding: function() {
        var i, len;

        // cache all sections in the DOM eligible to be the active section
        // also cache some jQobjs that we will refer to frequently
        this.$contentHeader = this.$contentHeader || $('header.reg-header');

        // sections that are eligible for being the active section
        this.$contentContainer = $('#' + this.id).find('li[id], .reg-section, .appendix-section, .supplement-section');

        // cache jQobjs of each reg section
        len = this.$contentContainer.length;

        // short term solution: sometimes, back buttoning on diffs, this.$sections undefined. why?
        this.$sections = this.$sections || {};

        for (i = 0; i < len; i++) {
            this.$sections[i] = $(this.$contentContainer[i]);
        }
    },

    route: function(options) {
        if (Router.hasPushState && typeof options.noRoute === 'undefined') {
            var url = this.url;

            // if a hash has been passed in
            if (options && typeof options.scrollToId !== 'undefined') {
                url += '#' + options.scrollToId;
                this.navigate(url);
                $('html, body').scrollTop($('#' + options.scrollToId).offset().top);
            } else {
                if (['diff', 'search-results'].indexOf(options.type) === -1) {
                    url += '#' + options.id;
                }
                this.navigate(url);
            }
        }
    },

    navigate: function(url) {
        Router.navigate(url);
        document.title = this.title;
    },

    remove: function() {
        $(window).off('scrollstop');
        this.stopListening();
        this.off();
        return this;
    },

    // lazy load images as the user scrolls
    loadImages: function() {
        $('.reg-image').lazyload();
    }
});

module.exports = ChildView;
