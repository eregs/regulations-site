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
    'click .activate-write': 'handleWriteLink',
    'click .citation.internal': 'openCitation',
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
        'table-of-contents-secondary',
    );
  },

  openCitation: function(e) {
    var $target = $(e.currentTarget);
    var hash = $target.attr('href');
    var id = $target.attr('data-section-id');
    var options = {};
    var type = this.options.type;
    var section = helpers.parsePreambleCitationId(hash, type);

    if (id) {
      e.preventDefault();

      MainEvents.trigger('section:open', section, options, type);
    }
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
      $dataTarget.data('indexes'),
      $dataTarget.data('label'),
      $section,
    );

    CommentEvents.trigger('comment:writeTabOpen');
  },

  handleWriteTab: function() {
    var $section = $('#' + this.section);

    this.write(
      $section.find('.activate-write').data('section'),
      $section.data('toc-id'),
      $section.data('indexes'),
      $section.find('.activate-write').data('label'),
      $section,
    );
  },

  cantWriteMessage: [
    'Your browser does not support localStorage, which is currently required',
    'to <em>submit</em> comments through this system. To find alternative',
    'comment submission methods, please read the agency instructions as',
    'listed in the preamble. We apologize for the inconvenience, but hope to',
    'remove this limitation soon.',
  ].join(' '),
  /**
   * We rely on localStorage for commenting at the moment. If it's not
   * available, let the user know. TODO: replace with Modernizr/similar
   **/
  checkCanWrite: function() {
    try {
      localStorage.setItem('_test', 'value');
      if (localStorage.getItem('_test') !== 'value') {
        MainEvents.trigger('section:error', this.cantWriteMessage);
      }
    } catch (e) {   // unfortunately, localStorage exception varies by browser
      MainEvents.trigger('section:error', this.cantWriteMessage);
    };
  },

  write: function(section, tocId, indexes, label, $parent) {
    this.mode = 'write';
    this.checkCanWrite();

    // Top-level sections and permalink sections use different markup;
    // find appropriate element on top-level sections. TODO: unify markup
    // and/or fetch excerpts asynchronously
    $parent = $parent.is('[data-page-type]') ?
      this.$read.find('.preamble-content') :
      $parent;

    $parent = $parent.clone();
    $parent.find('.activate-write').remove();

    if (section) {
      CommentEvents.trigger('comment:target', {
        section: section,
        tocId: tocId,
        indexes: indexes,
        label: label,
        $parent: $parent,
      });
    }

    this.$read.hide();
    this.$write.show();

    // set anchor to top of page
    $('body').scrollTop(0);
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
      docId: this.docId,
    });

    this.commentIndex = new CommentIndexView({
      el: this.$write.find('.comment-index'),
      docId: this.docId,
    });

    if (this.options.mode === 'write') {
      var $parent = $('#' + this.options.scrollToId);
      var indexes = $parent.data('indexes');

      this.write(this.options.section, this.options.tocId, indexes, this.options.label, $parent);
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
  },
});

module.exports = PreambleView;
