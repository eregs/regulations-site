

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');
const MainEvents = require('../../events/main-events');

Backbone.$ = $;

const HistoryView = Backbone.View.extend({

  el: '#timeline',

  events: {
    'click .version-link': 'setStorageItem',
  },

  initialize: function initialize() {
    this.listenTo(MainEvents, 'section:open', this.updateLinks);
    this.listenTo(MainEvents, 'diff:open', this.updateLinks);
  },

  setStorageItem: function setStorageItem() {
    sessionStorage.setItem('drawerDefault', 'timeline');
  },

  updateLinks: function updateLinks(initialSection) {
    let section = initialSection;
    let prefix = window.APP_PREFIX;
    if (typeof prefix !== 'undefined' && prefix.substr(prefix.length - 1) !== '/') {
      prefix += '/';
    }
    // section may not be defined (e.g. on the landing page)
    if (typeof section !== 'undefined') {
      this.$el.find('.version-link').each(function perLink() {
        const $link = $(this);
        $link.attr('href', `${prefix + section}/${$link.data('version')}`);
      });
      this.$el.find('.stop-button').each(function perButton() {
        const $link = $(this);
        /* Interpretations are split into "subterps" outside of diff view -
         * link to the first */
        if (section.indexOf('Interp') !== -1) {
          $link.attr('href', `${prefix + $link.data('first-subterp')}/${$link.data('version')}`);
        } else {
          $link.attr('href', `${prefix + section}/${$link.data('version')}`);
        }
      });

      /* diffs of interpretations are not currently more granular than the
       * whole interpretation */
      if (section.indexOf('Interp') !== -1) {
        section = `${section.split('-')[0]}-Interp`;
      }
      // update diff dropdown
      this.$el.find('.select-content form').each(function perForm() {
        const $form = $(this);
        // form action = diff_redirect/section/version
        const actionParts = _.compact($form.attr('action').split('/'));
        let actionPath = '';

        // remove section ID
        actionParts.splice(-2, 1, section);
        actionPath = `/${actionParts.join('/')}`;
        $form.attr('action', actionPath);
      });
    }
  },
});

module.exports = HistoryView;
