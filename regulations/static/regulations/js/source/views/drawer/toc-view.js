import storage from '../../redux/storage';
import { locationActiveEvt } from '../../redux/locationReduce';
import { activeSection } from '../../redux/reducers';

const $ = require('jquery');
const Backbone = require('backbone');
const Helpers = require('../../helpers');
const Router = require('../../router');
const MainEvents = require('../../events/main-events');
const HeaderEvents = require('../../events/header-events');
const Resources = require('../../resources.js');

Backbone.$ = $;

const TOCView = Backbone.View.extend({
  el: '#table-of-contents',

  events: {
    'click a.diff[data-section-id]': 'sendDiffClickEvent',
    'click a[data-section-id]:not(.diff)': 'sendClickEvent',
  },

  initialize: function initialize() {
    const openSection = $('section[data-page-type]').attr('id');

    storage().subscribe(this.updateFromRedux.bind(this));

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
    const newActiveLink = this.$el.find(`a[data-section-id="${tocId}"]`);
    const subpart = newActiveLink
                    .parent()
                    .prevAll('li[data-subpart-heading]')
                    .first()
                    .find('.toc-nav__divider')
                    .attr('data-section-id');

    this.$el.find('.current').removeClass('current');
    newActiveLink.addClass('current');

    if (subpart && subpart.length > 0) {
      HeaderEvents.trigger('subpart:present', Helpers.formatSubpartLabel(subpart));
    } else {
      HeaderEvents.trigger('subpart:absent');
    }

    return this;
  },

  updateFromRedux: function updateFromRedux() {
    this.setActive(activeSection(storage()));
  },

    // **Event trigger**
    // when a TOC link is clicked, send an event along with the href of the clicked link
  sendClickEvent: function sendClickEvent(e) {
    e.preventDefault();

    const sectionId = $(e.currentTarget).data('section-id');
    const type = this.$el.closest('.panel').data('page-type');
    storage().dispatch(locationActiveEvt(sectionId));
    MainEvents.trigger('section:open', sectionId, {}, type);
  },

  sendDiffClickEvent: function sendDiffClickEvent(e) {
    e.preventDefault();

    const $link = $(e.currentTarget);
    const sectionId = $link.data('section-id');
    const config = {};

    config.newerVersion = Helpers.findDiffVersion(Resources.versionElements);
    config.baseVersion = Helpers.findVersion(Resources.versionElements);
    storage().dispatch(locationActiveEvt(sectionId));
    MainEvents.trigger('diff:open', sectionId, config, 'diff');
  },

    // **Inactive**
    // Intended to keep the active link in view as the user moves around the doc
  scrollToActive: function scrollToActive() {
    const activeLink = document.querySelectorAll('#table-of-contents .current');

    if (activeLink[0]) {
      activeLink[0].scrollIntoView();
    }
  },
});

module.exports = TOCView;
