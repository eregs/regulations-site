

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');
require('../../events/scroll-stop.js');
const Router = require('../../router');
const HeaderEvents = require('../../events/header-events');
const DrawerEvents = require('../../events/drawer-events');
const MainEvents = require('../../events/main-events');
const GAEvents = require('../../events/ga-events');

Backbone.$ = $;

// Adjust the offset of how far past the section top before the wayfinder
// changes. Based on 2 * line-height + padding-top.
const WAYFINDER_SCROLL_OFFSET = window.WAYFINDER_SCROLL_OFFSET || 64;

const ChildView = Backbone.View.extend({
  el: '#content-wrapper',

  initialize: function initialize(options) {
    this.options = options;
    this.$topSection = this.$el.find('[data-page-type]');
    this.sectionLabel = this.$topSection.data('label');
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

    this.activeSection = this.options.id;
    this.$activeSection = $('#' + this.activeSection);

    this.loadImages();
  },

  attachWayfinding: function attachWayfinding() {
    this.updateWayfinding();
        // * when a scroll event completes, check what the active secion is
        // we can't scope the scroll to this.$el because there's no localized
        // way to grab the scroll event, even with overflow:scroll
    $(window).on('scrollstop', (_.bind(this.checkActiveSection, this)));
  },

  render: function render() {
    this.updateWayfinding();
    this.loadImages();
    this.scroll();
    HeaderEvents.trigger('section:open', this.sectionLabel);
    DrawerEvents.trigger('section:open', this.id);
  },

  scroll: function scroll() {
    let offsetTop;
    let $scrollToId;
    if (this.options.scrollToId) {
      $scrollToId = $('#' + this.options.scrollToId);
      if ($scrollToId.length) {
        offsetTop = $scrollToId.offset().top;
      }
      window.scrollTo(0, offsetTop || 0);
    }
  },

  changeFocus: function changeFocus(id) {
    $(id).focus();
  },

  assembleTitle: function assembleTitle() {
    const titleParts = _.compact(document.title.split(' '));
    const newTitle = [titleParts[0], titleParts[1], this.sectionLabel, '|', 'eRegulations'];
    return newTitle.join(' ');
  },

    // naive way to update the active table of contents link and wayfinding header
    // once a scroll event ends, we loop through each content section DOM node
    // the first one whose offset is greater than the window scroll position, accounting
    // for the fixed position header (via margin/border offsets), is deemed the
    // active section
  checkActiveSection: function checkActiveSection() {
    $.each(this.$sections, (idx, $section) => {
      if ($section.offset().top + WAYFINDER_SCROLL_OFFSET >= $(window).scrollTop()) {
        if (_.isEmpty(this.activeSection) || (this.activeSection !== $section.id)) {
          this.activeSection = $section[0].id;
          this.$activeSection = $($section[0]);
            // **Event** trigger active section change
          HeaderEvents.trigger('section:open', this.$activeSection.data('label'));
          DrawerEvents.trigger('section:open', this.$activeSection.data('toc-id') || this.id);
          MainEvents.trigger('paragraph:active', this.activeSection);

          if (typeof window.history !== 'undefined' && typeof window.history.replaceState !== 'undefined') {
              // update hash in url
            window.history.replaceState(
                null,
                null,
                window.location.origin + window.location.pathname + window.location.search + '#' + this.activeSection,
              );
          }

          return false;
        }
      }
      return true;
    });
  },

  updateWayfinding: function updateWayfinding() {
      // cache all sections in the DOM eligible to be the active section
      // also cache some jQobjs that we will refer to frequently.
      //
      // Sections that are eligible for being the active section.
    this.$sections = this.$el
        .find('li[id], .reg-section, .appendix-section, .supplement-section')
        .map((idx, elm) => $(elm));
  },

  route: function route(options) {
    if (Router.hasPushState && typeof options.noRoute === 'undefined') {
      let url = this.url;

            // if a hash has been passed in
      if (options && options.scrollToId) {
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

  navigate: function navigate(url) {
    Router.navigate(url);
    MainEvents.trigger('route', url);
    document.title = this.title;
  },

  remove: function remove() {
    $(window).off('scrollstop');
    this.stopListening();
    this.off();
    return this;
  },

    // lazy load images as the user scrolls
  loadImages: function loadImages() {
    $('.reg-image').lazyload();
  },
});

module.exports = ChildView;
