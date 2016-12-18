'use strict';

var $ = require('jquery');
var Backbone = require('backbone');
var Helpers = require('../../helpers');
var Router = require('../../router');
var MainEvents = require('../../events/main-events');
var DrawerEvents = require('../../events/drawer-events');
var HeaderEvents = require('../../events/header-events');
var Resources = require('../../resources.js');

Backbone.$ = $;

var TOCView = Backbone.View.extend({
  el: '#table-of-contents',

  events: {
    'click a.diff[data-section-id]': 'sendDiffClickEvent',
    'click a[data-section-id]:not(.diff)': 'sendClickEvent',
  },

  initialize: function initialize() {
    var openSection = $('section[data-page-type]').attr('id');

    this.listenTo(DrawerEvents, 'section:open', this.setActive);

    if (openSection) {
      this.setActive(openSection);
    }

        // **TODO** need to work out a bug where it scrolls the content section
        // $('#menu-link:not(.active)').on('click', this.scrollToActive);

        // if the browser doesn't support pushState, don't
        // trigger click events for links
    if (Router.hasPushState === false) {
      this.events = {};
    }
  },

  // update active classes, find new active based on the reg entity id in the anchor
  setActive: function setActive(tocId) {
    var newActiveLink;
    var subpart;

    newActiveLink = this.$el.find('a[data-section-id="' + tocId + '"]');

    this.$el.find('.current').removeClass('current');
    newActiveLink.addClass('current');
    subpart = newActiveLink
                    .parent()
                    .prevAll('li[data-subpart-heading]')
                    .first()
                    .find('.toc-nav__divider')
                    .attr('data-section-id');

    if (subpart && subpart.length > 0) {
      HeaderEvents.trigger('subpart:present', Helpers.formatSubpartLabel(subpart));
    } else {
      HeaderEvents.trigger('subpart:absent');
    }

    return this;
  },

    // **Event trigger**
    // when a TOC link is clicked, send an event along with the href of the clicked link
  sendClickEvent: function sendClickEvent(e) {
    e.preventDefault();

    var sectionId = $(e.currentTarget).data('section-id');
    var type = this.$el.closest('.panel').data('page-type');
    DrawerEvents.trigger('section:open', sectionId);
    MainEvents.trigger('section:open', sectionId, {}, type);
  },

  sendDiffClickEvent: function sendDiffClickEvent(e) {
    e.preventDefault();

    var $link = $(e.currentTarget);
    var sectionId = $link.data('section-id');
    var config = {};

    config.newerVersion = Helpers.findDiffVersion(Resources.versionElements);
    config.baseVersion = Helpers.findVersion(Resources.versionElements);
    DrawerEvents.trigger('section:open', sectionId);
    MainEvents.trigger('diff:open', sectionId, config, 'diff');
  },

    // **Inactive**
    // Intended to keep the active link in view as the user moves around the doc
  scrollToActive: function scrollToActive() {
    var activeLink = document.querySelectorAll('#table-of-contents .current');

    if (activeLink[0]) {
      activeLink[0].scrollIntoView();
    }
  },
});

module.exports = TOCView;
