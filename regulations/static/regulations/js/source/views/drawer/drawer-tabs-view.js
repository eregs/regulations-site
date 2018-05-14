import storage from '../../redux/storage';
import { activePane } from '../../redux/reducers';
import { paneActiveEvt } from '../../redux/paneReduce';

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');
const GAEvents = require('../../events/ga-events');
const MainEvents = require('../../events/main-events');

Backbone.$ = $;

const DrawerTabsView = Backbone.View.extend({
  el: '.toc-head',

  events: {
    'click .toc-toggle': 'openDrawer',
    'click .toc-nav-link': 'updatePaneTabs',
  },

  idMap: {
    'table-of-contents': '#menu-link',
    'table-of-contents-secondary': '#table-of-contents-secondary-link',
    timeline: '#timeline-link',
    search: '#search-link',
  },

  initialize: function initialize(options) {
    this.previousTab = activePane(storage());
    storage().subscribe(this.handleReduxUpdate.bind(this));
    this.$activeEls = $('#menu, #site-header, #content-body, #primary-footer, #content-header');

        // view switcher buttons - TOC, calendar, search
    this.$tocLinks = $('.toc-nav-link');
    this.$toggleArrow = $('#panel-link');

        // default the drawer state to close
    this.drawerState = 'close';

        // For browser widths above 1100px apply the 'open' class
        //  and set drawer state to open
    if (options.forceOpen || document.documentElement.clientWidth > 1100) {
      this.$toggleArrow.addClass('open');
      this.drawerState = 'open';
    }

    this.$activeEls.addClass(this.drawerState);
  },

  handleReduxUpdate: function handleReduxUpdate() {
    const tab = activePane(storage());
    this.$tocLinks.removeClass('current');
    $(this.idMap[tab]).addClass('current');
    if (tab !== this.previousTab) {
      GAEvents.trigger('drawer:switchTab', {
        id: tab,
        type: 'drawer',
      });
    }
    this.previousTab = tab;
  },

  // this.$activeEls are structural els that need to have
  // CSS applied to work with the drawer conditionally based
  // on its state
  updateDOMState: function updateDOMState() {
    if (typeof this.$activeEls !== 'undefined') {
      this.$activeEls.toggleClass(this.drawerState);
    }
  },

  openDrawer: function openDrawer(e) {
    const context = { type: 'drawer' };

    if (e) {
      e.preventDefault();
    }

    this.toggleDrawerState();

        // only send click event if there was an actual click
    if (e) {
      if ($(e.target).hasClass('open')) {
        GAEvents.trigger('drawer:open', context);
      } else {
        GAEvents.trigger('drawer:close', context);
      }
      MainEvents.trigger('section:resize', context);
    }
  },

    // figure out whether drawer should open/close
    // tell surrounding elements to update accordingly
    // update the open/close arrow
    // set state
  toggleDrawerState: function toggleDrawerState() {
    const state = (this.drawerState === 'open') ? 'close' : 'open';
    this.updateDOMState();
    this.$toggleArrow.toggleClass('open');
    this.drawerState = state;
    this.updateDOMState();
  },

    // update active pane based on click or external input
  updatePaneTabs: function updatePaneTabs(e) {
    e.preventDefault();

    const $target = $(e.target);
    const linkValue = _.last($target.closest('a').attr('href').split('#'));
    this.activePane = linkValue;

    if ($('.panel').css('left') === '-200px') {
      this.openDrawer();
    }

    storage().dispatch(paneActiveEvt(linkValue));
  },
});

module.exports = DrawerTabsView;
