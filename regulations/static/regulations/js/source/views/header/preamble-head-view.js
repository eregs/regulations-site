'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var PreambleHeadView = Backbone.View.extend({
  el: '.preamble-header',

  events: {
    'click .read-proposal': 'readProposal',
    'click .write-comment': 'writeComment'
  },

  initialize: function() {
    this.$readTab = this.$el.find('.read-proposal');
    this.$writeTab = this.$el.find('.write-comment');

    Backbone.on('writeSectionComment', this.writeComment, this);
  },

  readProposal: function() {
    this.$readTab.addClass('active-mode');
    this.$writeTab.removeClass('active-mode');

    Backbone.trigger('readProposal');
  },

  writeComment: function() {
    this.$writeTab.addClass('active-mode');
    this.$readTab.removeClass('active-mode');
  }

});

module.exports = PreambleHeadView;
