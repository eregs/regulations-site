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
var DrawerEvents = require('../../events/drawer-events');
var starsHelpers = require('./stars-helpers');
var helpers = require('../../helpers');

var PreambleView = ChildView.extend({
  events: {
    'click .activate-write': 'handleWriteLink'
  },

  initialize: function(options) {
    this.options = options;

    var parsed = helpers.parsePreambleId(this.options.id);
    var type = parsed.type;

    this.options.scrollToId = parsed.hash;
    this.url = parsed.path.join('/');

    ChildView.prototype.initialize.apply(this, arguments);
    this.renderComments();

    this.listenTo(CommentEvents, 'read:proposal', this.handleRead);
    this.listenTo(CommentEvents, 'comment:write', this.handleWriteTab);
    this.listenTo(MainEvents, 'paragraph:active', this.handleParagraphActive);

    CommentEvents.trigger('comment:readTabOpen');

    DrawerEvents.trigger(
      'pane:init',
      parsed.type === 'preamble' ?
        'table-of-contents' :
        'table-of-contents-secondary'
    );
  },

  handleRead: function() {
    this.mode = 'read';
    this.$write.hide();
    this.$read.show();
  },

  handleParagraphActive: function(id) {
    // update current Section ID as active paragraph changes
    this.section = id;
  },

  handleWriteLink: function(e) {
    var $target = $(e.target);
    var $dataTarget = $target.closest('.activate-write');
    var $section = $target.closest('[data-permalink-section]');

    this.write(
      $dataTarget.data('section'),
      $section.data('toc-id'),
      $dataTarget.data('label'),
      $section
    );

    CommentEvents.trigger('comment:writeTabOpen');
  },

  handleWriteTab: function() {
    var $section = $('#' + this.section);

    this.write(
      $section.find('.activate-write').data('section'),
      $section.data('toc-id'),
      $section.find('.activate-write').data('label'),
      $section
    );
  },

  write: function(section, tocId, label, $parent) {
    this.mode = 'write';
    $parent = $parent.clone();
    $parent.find('.activate-write').remove();

    CommentEvents.trigger('comment:target', {
      section: section,
      tocId: tocId,
      label: label,
      $parent: $parent
    });
    this.$read.hide();
    this.$write.show();
  },

  renderComments: function() {
    this.mode = 'read';
    this.$read = this.$el.find('#preamble-read');
    this.$write = this.$el.find('#preamble-write');

    this.section = this.$read.find('[data-permalink-section]').attr('id');
    this.docId = this.$read.closest('section').data('doc-id');

    this.preambleHeadView = new PreambleHeadView();

    this.commentView = new CommentView({
      el: this.$write.find('.comment-wrapper'),
      section: this.section,
      docId: this.docId
    });

    this.commentIndex = new CommentIndexView({
      el: this.$write.find('.comment-index'),
      docId: this.docId
    });

    if (this.options.mode === 'write') {
      var $parent = $('#' + this.options.scrollToId);
      this.write(this.options.section, this.options.tocId, this.options.label, $parent);
    } else {
      this.handleRead();
    }
    this.collapseStars();
  },

  collapseStars: function() {
    var $expander;
    this.$el.find('li[data-stars]').each(function(idx, elt) {
      var $li = $(elt);
      var starType = $li.data('stars');
      $expander = starsHelpers[starType]($li, $expander);
    });
  },

  remove: function() {
    this.commentView.remove();
    this.commentIndex.remove();
    Backbone.View.prototype.remove.call(this);
  },

  /**
   * Update section in viewport if in read mode.
   */
  checkActiveSection: function() {
    if (this.mode === 'read') {
      ChildView.prototype.checkActiveSection.call(this);
    }
  }
});

module.exports = PreambleView;
