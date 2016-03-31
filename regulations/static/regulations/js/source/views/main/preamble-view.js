'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var ChildView = require('./child-view');
var MainEvents = require('../../events/main-events');
var PreambleHeadView = require('../header/preamble-head-view');
var CommentView = require('../comment/comment-view');
var CommentIndexView = require('../comment/comment-index-view');
var CommentEvents = require('../../events/comment-events');

var PreambleView = ChildView.extend({
  el: '#content-wrapper',

  events: {
    'click .activate-write': 'handleWrite'
  },

  initialize: function(options) {
    this.options = options;
    this.id = options.id;
    this.url = 'preamble/' + this.id.split('-').join('/');

    if (!options.render) {
      this.render();
    }

    ChildView.prototype.initialize.apply(this, arguments);

    this.listenTo(CommentEvents, 'read:proposal', this.handleRead);
    this.listenTo(CommentEvents, 'comment:write', this.handleWrite);
    this.listenTo(MainEvents, 'paragraph:active', this.handleParagraphActive);

    CommentEvents.trigger('comment:readTabOpen');
  },

  handleRead: function() {
    this.$write.hide();
    this.$read.show();
  },

  handleParagraphActive: function(id) {
    // update current Section ID as active paragraph changes
    this.currentSectionId = id;
  },

  handleWrite: function(e) {
    // + Write a comment about section (link)
    if (e) {
      var $target = $(e.target);
      this.write(
        $target.data('section'),
        $target.data('label'),
        $target.closest('[data-permalink-section]')
      );

      CommentEvents.trigger('comment:writeTabOpen');
    }
    // Write a comment tab
    else {
      var $section = $('#' + this.currentSectionId);

      this.write(
        this.currentSectionId,
        $section.find('.activate-write').data('label'),
        $section
      );
    }
  },

  write: function(section, label, $parent) {
    $parent = $parent.clone();
    $parent.find('.activate-write').remove();
    CommentEvents.trigger('comment:target', {
      section: section,
      label: label,
      $parent: $parent
    });
    this.$read.hide();
    this.$write.show();
  },

  render: function() {
    ChildView.prototype.render.apply(this, arguments);

    this.$read = this.$el.find('#preamble-read');
    this.$write = this.$el.find('#preamble-write');

    this.currentSectionId = this.$read.closest('section').attr('id');
    this.docId = this.currentSectionId.split('-')[0];

    this.preambleHeadView = new PreambleHeadView();

    this.commentView = new CommentView({
      el: this.$write.find('.comment-wrapper'),
      section: this.section
    });

    this.commentIndex = new CommentIndexView({
      el: this.$write.find('.comment-index'),
      docId: this.docId
    });

    if (this.options.mode === 'write') {
      var $parent = $('#' + this.options.section).find('[data-permalink-section]');
      this.write(this.options.section, this.options.label, $parent);
    } else {
      this.handleRead();
    }
  },

  remove: function() {
    this.commentView.remove();
    this.commentIndex.remove();
    Backbone.View.prototype.remove.call(this);
  }
});

module.exports = PreambleView;
