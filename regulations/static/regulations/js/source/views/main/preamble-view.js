import storage from '../../redux/storage';
import { activeParagraph } from '../../redux/reducers';
import { paneActiveEvt } from '../../redux/paneReduce';

const $ = require('jquery');
const Backbone = require('backbone');

Backbone.$ = $;

const ChildView = require('./child-view');
const MainEvents = require('../../events/main-events');
const PreambleHeadView = require('../header/preamble-head-view');
const CommentView = require('../comment/comment-view');
const CommentIndexView = require('../comment/comment-index-view');
const CommentEvents = require('../../events/comment-events');
const starsHelpers = require('./stars-helpers');
const helpers = require('../../helpers');

const PreambleView = ChildView.extend({
  events: {
    'click .activate-write': 'handleWriteLink',
    'click .citation.internal': 'openCitation',
  },

  initialize: function initialize(options, ...args) {
    this.options = options;

    const parsed = helpers.parsePreambleId(this.options.id);

    this.options.scrollToId = parsed.hash;

    this.url = parsed.path.join('/');

    ChildView.prototype.initialize.apply(this, [options].concat(args));
    this.renderComments();

    this.listenTo(CommentEvents, 'read:proposal', this.handleRead);
    this.listenTo(CommentEvents, 'comment:write', this.handleWriteTab);
    storage().subscribe(this.handleParagraphActive.bind(this));

    CommentEvents.trigger('comment:readTabOpen');

    storage().dispatch(paneActiveEvt(
      parsed.type === 'preamble' ?
        'table-of-contents' :
        'table-of-contents-secondary',
    ));
  },

  openCitation: function openCitation(e) {
    const $target = $(e.currentTarget);
    const hash = $target.attr('href');
    const id = $target.attr('data-section-id');
    const options = {};
    const type = this.options.type;
    const section = helpers.parsePreambleCitationId(hash, type);

    if (id) {
      e.preventDefault();

      MainEvents.trigger('section:open', section, options, type);
    }
  },

  handleRead: function handleRead() {
    this.mode = 'read';
    this.$write.hide();
    this.$read.show();
  },

  handleParagraphActive: function handleParagraphActive() {
    // update current Section ID as active paragraph changes
    this.section = activeParagraph(storage());
  },

  handleWriteLink: function handleWriteLink(e) {
    const $target = $(e.target);
    const $dataTarget = $target.closest('.activate-write');
    const $section = $target.closest('[data-permalink-section]');

    this.write(
      $dataTarget.data('section'),
      $section.data('toc-id'),
      $dataTarget.data('indexes'),
      $dataTarget.data('label'),
      $section,
    );

    CommentEvents.trigger('comment:writeTabOpen');
  },

  handleWriteTab: function handleWriteTab() {
    const $section = $(`#${this.section}`);

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
  checkCanWrite: function checkCanWrite() {
    try {
      localStorage.setItem('_test', 'value');
      if (localStorage.getItem('_test') !== 'value') {
        MainEvents.trigger('section:error', this.cantWriteMessage);
      }
    } catch (e) {   // unfortunately, localStorage exception varies by browser
      MainEvents.trigger('section:error', this.cantWriteMessage);
    }
  },

  write: function write(section, tocId, indexes, label, parentEl) {
    let $parent = parentEl;
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
        section,
        tocId,
        indexes,
        label,
        $parent,
      });
    }

    this.$read.hide();
    this.$write.show();

    // set anchor to top of page
    $('body').scrollTop(0);
  },

  renderComments: function renderComments() {
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
      const $parent = $(`#${this.options.scrollToId}`);
      const indexes = $parent.data('indexes');

      this.write(this.options.section, this.options.tocId, indexes, this.options.label, $parent);
    } else {
      this.handleRead();
    }
    this.collapseStars();
  },

  collapseStars: function collapseStars() {
    let $expander;
    this.$el.find('li[data-stars]').each((idx, elt) => {
      const $li = $(elt);
      const starType = $li.data('stars');
      $expander = starsHelpers[starType]($li, $expander);
    });
  },

  remove: function remove() {
    this.commentView.remove();
    this.commentIndex.remove();
    Backbone.View.prototype.remove.call(this);
  },

  /**
   * Update section in viewport if in read mode.
   */
  checkActiveSection: function checkActiveSection() {
    if (this.mode === 'read') {
      ChildView.prototype.checkActiveSection.call(this);
    }
  },
});

module.exports = PreambleView;
