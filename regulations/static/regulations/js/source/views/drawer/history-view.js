'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
var MainEvents = require('../../events/main-events');

Backbone.$ = $;

var HistoryView = Backbone.View.extend({

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

  updateLinks: function updateLinks(section) {
    var prefix = window.APP_PREFIX;
    if (typeof prefix !== 'undefined' && prefix.substr(prefix.length - 1) !== '/') {
      prefix = prefix + '/';
    }
        // section may not be defined (e.g. on the landing page)
    if (typeof section !== 'undefined') {
      this.$el.find('.version-link').each(function perLink() {
        var $link = $(this);
        $link.attr('href', prefix + section + '/' + $link.data('version'));
      });
      this.$el.find('.stop-button').each(function perButton() {
        var $link = $(this);
        /* Interpretations are split into "subterps" outside of diff view -
         * link to the first */
        if (section.indexOf('Interp') !== -1) {
          $link.attr('href', prefix + $link.data('first-subterp') + '/' + $link.data('version'));
        } else {
          $link.attr('href', prefix + section + '/' + $link.data('version'));
        }
      });

      /* diffs of interpretations are not currently more granular than the
       * whole interpretation */
      if (section.indexOf('Interp') !== -1) {
        section = section.split('-')[0] + '-Interp';
      }
            // update diff dropdown
      this.$el.find('.select-content form').each(function perForm() {
        var $form = $(this),
          actionParts,
          actionPath;

                // form action = diff_redirect/section/version
        actionParts = _.compact($form.attr('action').split('/'));
                // remove section ID
        actionParts.splice(-2, 1, section);
        actionPath = '/' + actionParts.join('/');
        $form.attr('action', actionPath);
      });
    }
  },
});

module.exports = HistoryView;
