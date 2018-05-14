import storage from '../../redux/storage';
import { locationActiveEvt } from '../../redux/locationReduce';
import { paneActiveEvt } from '../../redux/paneReduce';

const $ = require('jquery');
const _ = require('underscore');
const URI = require('urijs');
require('datatables.net')();
const Clipboard = require('clipboard');
const Backbone = require('backbone');
const SearchResultsView = require('./search-results-view');
const RegView = require('./reg-view');
const RegModel = require('../../models/reg-model');
const SearchModel = require('../../models/search-model');
const SectionFooter = require('./section-footer-view');
const MainEvents = require('../../events/main-events');
const SidebarEvents = require('../../events/sidebar-events');
const DiffModel = require('../../models/diff-model');
const PreambleModel = require('../../models/preamble-model');
const DiffView = require('./diff-view');
const Router = require('../../router');
const HeaderEvents = require('../../events/header-events');
const Helpers = require('../../helpers');
const CommentReviewView = require('../comment/comment-review-view');
const CommentConfirmView = require('../comment/comment-confirm-view');
const PreambleView = require('./preamble-view');
const Resources = require('../../resources');

Backbone.$ = $;

const MainView = Backbone.View.extend({
  el: '#content-body',

  events: {
    'click .toggle .button': 'toggleElement',
  },

  /**
   * Toggle an element
   *
   * An element that contains class 'toggle'
   * will toggle class 'collapsible' via 'button' class
   * as well as toggle button open/close elements for labeling purposes.
   * Also toggles aria-hidden/expanded attributes for accessibility.
   *
   * <div class="toggle">
   *  <div class="collapsible" aria-hidden="true"></div>
   *  <div class="button" aria-expanded="false">
   *   <div class="toggle-button-open" aria-hidden="false">Open</div>
   *   <div class="toggle-button-close" aria-hidden="true">Close</div>
   *  </div>
   * </div>
   *
   */
  toggleElement: function toggleElement(e) {
    const $target = $(e.target);
    const $toggleEl = $target.closest('.toggle');
    const $collapsibleEl = $toggleEl.find('.collapsible');
    const $toggleButton = $toggleEl.find('.button');
    const $toggleButtonOpen = $toggleButton.find('.toggle-button-open');
    const $toggleButtonClose = $toggleButton.find('.toggle-button-close');

    e.preventDefault();

    if ($collapsibleEl.is(':visible')) {
      $collapsibleEl.hide();
      $collapsibleEl.attr('aria-hidden', true);

      $toggleButton.attr('aria-expanded', false);

      $toggleButtonOpen.show();
      $toggleButtonOpen.attr('aria-hidden', false);
      $toggleButtonClose.hide();
      $toggleButtonClose.attr('aria-hidden', true);
    } else {
      $collapsibleEl.show();
      $collapsibleEl.attr('aria-hidden', false);

      $toggleButton.attr('aria-expanded', true);

      $toggleButtonClose.show();
      $toggleButtonClose.attr('aria-hidden', false);
      $toggleButtonOpen.hide();
      $toggleButtonOpen.attr('aria-hidden', true);
    }
  },

  initialize: function initialize() {
    this.dataTables = null;

    if (Router.hasPushState) {
      this.listenTo(MainEvents, 'search-results:open', this.openSection);
      this.listenTo(MainEvents, 'section:open', this.openSection);
      this.listenTo(MainEvents, 'diff:open', this.openSection);
      this.listenTo(MainEvents, 'breakaway:open', this.breakawayOpen);
      this.listenTo(MainEvents, 'section:error', this.displayError);
    }
    this.listenTo(MainEvents, 'section:resize', this.applyTablePlugin);
    this.listenTo(MainEvents, 'section:setHandlers', this.setHandlers);

    this.$topSection = this.$el.find('section[data-page-type]');

      // which page are we starting on?
    this.contentType = this.$topSection.data('page-type');
      // what version of the reg?
    this.regVersion = Helpers.findVersion(Resources.versionElements);
      // what section do we have open?
    this.sectionId = this.$topSection.attr('id') ||
        this.$topSection.find('section[id]').attr('id');
    this.docId = $('#menu').data('doc-id');
    this.cfrTitle = $('#menu').data('cfr-title-number');

    this.childModel = this.modelmap[this.contentType];
    if (this.sectionId && this.childModel) {
        // store the contents of our $el in the model so that we
        // can re-render it later
      this.modelmap[this.contentType].set(this.sectionId, this.$el.html());
    }

    const options = {
      subContentType: this.isAppendixOrSupplement(),
      render: false,
    };

    if (this.contentType === 'search-results') {
      options.params = URI.parseQuery(window.location.search);
      options.query = options.params.q;
    }

    this.setChildOptions(options);

    if (this.contentType === 'landing-page') {
      storage().dispatch(paneActiveEvt('table-of-contents'));
    }

    this.renderSection(null);

      // hide toggle elements
    $('.toggle .collapsible').attr('aria-hidden', 'true').hide();
    $('.toggle .toggle-button-close').attr('aria-hidden', 'true').hide();
  },

  modelmap: {
    'reg-section': RegModel,
    'landing-page': RegModel,
    'search-results': SearchModel,
    diff: DiffModel,
    appendix: RegModel,
    interpretation: RegModel,
    'preamble-section': PreambleModel,
  },

  viewmap: {
    'reg-section': RegView,
    'landing-page': RegView,
    'search-results': SearchResultsView,
    diff: DiffView,
    appendix: RegView,
    interpretation: RegView,
    'comment-review': CommentReviewView,
    'comment-confirm': CommentConfirmView,
    'preamble-section': PreambleView,
  },

  openSection: function openSection(id, options, type) {
      // Close breakaway if open
    if (typeof this.breakawayCallback !== 'undefined') {
      this.breakawayCallback();
      delete (this.breakawayCallback);
    }

    this.contentType = type;

      // id is null on search results as there is no section id
    if (id !== null) {
      this.sectionId = id;
    }

    if (this.childView) {
      this.childView.remove();
      delete (this.childView);
    }

    this.loading();
    SidebarEvents.trigger('section:loading');

    this.childModel = this.modelmap[this.contentType];
    this.setChildOptions(_.extend({ render: true }, options));

    this.childModel.get(id, this.childOptions)
        .then(this.renderSection.bind(this))
        .fail(this.renderError.bind(this));
  },

  setChildOptions: function setChildOptions(options) {
    this.childOptions = _.extend({
      id: this.sectionId,
      type: this.contentType,
      regVersion: this.regVersion,
      docId: this.docId,
      model: this.childModel,
      cfrTitle: this.cfrTitle,
    }, options);

      // Diffs need some more version context
    if (this.contentType === 'diff') {
      this.childOptions.baseVersion = this.regVersion || Helpers.findVersion(
        Resources.versionElements);
      this.childOptions.newerVersion = Helpers.findDiffVersion(Resources.versionElements);
      if (typeof options.fromVersion === 'undefined') {
        this.childOptions.fromVersion = $('#table-of-contents').data('from-version');
      }
    }

      // Search needs to know which version to search and switch to that version
    if (this.contentType === 'search-results' && typeof options.searchVersion !== 'undefined') {
      this.childOptions.regVersion = options.searchVersion;
    }
  },

  renderSection: function renderSection(html) {
    if (html) {
      this.$el.html(html);
    }

    this.childOptions.el = this.$el.children().get(0);

    if (this.contentType) {
      this.childView = new this.viewmap[this.contentType](this.childOptions);
    }

      // Destroy and recreate footer
    if (this.sectionFooter) {
      this.sectionFooter.remove();
    }
    const $footer = this.$el.find('.section-nav');
    if ($footer) {
      this.sectionFooter = new SectionFooter({ el: $footer });
    }

    SidebarEvents.trigger('update', {
      type: this.contentType,
      id: this.sectionId,
    });

    this.loaded();
  },

  renderError: function renderError() {
    MainEvents.trigger('section:error');
  },

  isAppendixOrSupplement: function isAppendixOrSupplement() {
    if (Helpers.isAppendix(this.sectionId)) {
      return 'appendix';
    } else if (Helpers.isSupplement(this.sectionId)) {
      return 'supplement';
    }
    return false;
  },

  breakawayOpen: function breakawayOpen(cb) {
    this.breakawayCallback = cb;
    this.loading();
  },

  displayError: function displayError(message = 'Due to a network error, we were unable to retrieve the requested information.') {
    // Prevent error warning stacking
    $('.error-network').remove();

    // Get ID of still rendered last section
    const $old = this.$el.find('section[data-page-type]');
    const oldId = $old.attr('id');
    const oldLabel = $old.data('label');
    const $error = this.$el
          .prepend(
            `${'<div class="error error-network">' +
              '<span class="cf-icon cf-icon-error icon-warning"></span>'}${
              message
            }</div>`,
          )
          .hide()
          .fadeIn('slow');

    storage().dispatch(locationActiveEvt(oldId));
    HeaderEvents.trigger('section:open', oldLabel);

    this.loaded();
    SidebarEvents.trigger('section:error');

    window.scrollTo($error.offset().top, 0);
  },

  loading: function loading() {
        // visually indicate that a new section is loading
    $('.main-content').addClass('loading');
  },

  loaded: function loaded() {
        // change focus to main content area when new sections are loaded
    $('.main-content').removeClass('loading').focus();
    this.setHandlers();
  },

  setHandlers: function setHandlers() {
    this.applyTablePlugin();
    this.applyClipboardPlugin();
  },

  applyClipboardPlugin: function applyClipboardPlugin() {
    // Create anchor tag for copy to clipboard
    if (document.queryCommandSupported('copy')) {
      this.$el.find('*[data-copyable="true"]').each((index, copyable) => {
        const link = $('<a>', {
          class: 'clipboard-link',
          text: 'Copy this text to your clipboard',
          title: 'Copy this text to your clipboard',
          id: `#copyable-${index}`,
          href: `#copyable-${index}`,
        });
        // Can we avoid `new` here?
        /* eslint-disable no-new */
        new Clipboard(link[0], {
          target: function target() {
            return copyable;
          },
        });
        /* eslint-enable */
        $(copyable).before(link);
      });
    }
  },

  applyTablePlugin: function applyTablePlugin() {
    if (this.dataTables) {
      this.dataTables.destroy();
    }
        // Only apply the datatables plugin if there is a table header present
    if (this.$el.find('table').length) {
      this.dataTables = this.$el.find('table').has('thead *').DataTable({
        paging: false,
        searching: false,
        scrollY: 400,
        scrollCollapse: true,
        scrollX: true,
        info: false,
      });
    }
  },
});
module.exports = MainView;
