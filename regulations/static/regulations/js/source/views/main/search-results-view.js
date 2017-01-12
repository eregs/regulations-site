import storage from '../../redux/storage';
import { paneActiveEvt } from '../../redux/paneReduce';

const $ = require('jquery');
const Backbone = require('backbone');
const Router = require('../../router');
const HeaderEvents = require('../../events/header-events');
const MainEvents = require('../../events/main-events');
const ChildView = require('./child-view');

Backbone.$ = $;

const SearchResultsView = ChildView.extend({
  events: {
    'click .search-nav a': 'paginate',
    'click h3 .internal': 'openResult',
  },

  initialize: function initialize(options, ...args) {
    this.options = options;
    this.query = this.options.query;
    // the TOC may link to a different reg version than this.options.resultsRegVersion
    // because the user can select a different version to pull search results from
    this.resultsRegVersion = this.options.regVersion;
    this.page = parseInt(this.options.page, 10) || 0;
    this.title = `Search of ${this.options.docId} for ${this.query} | eRegulations`;

    // if the browser doesn't support pushState, don't
    // trigger click events for links
    if (Router.hasPushState === false) {
      this.events = {};
    }

    storage().dispatch(paneActiveEvt('search'));

    // if the site wasn't loaded on the search results page
    if (this.options.render) {
      this.url = `search/${this.model.assembleSearchURL(this.options)}`;
      ChildView.prototype.initialize.apply(this, [options].concat(args));
    } else {
      this.options.docType = this.$el.data('doc-type');
    }
  },

  setElement: function setElement() {
    Backbone.View.prototype.setElement.call(this, '#content-wrapper.search-results');
  },

  render: function render() {
    const $results = this.$el.find('#result-count');

        // if the results were ajaxed in, update header
    if ($results.text().length > 0) {
      HeaderEvents.trigger('search-results:open', $results.text());
      $results.remove();
    }

    if (Router.hasPushState) {
      if (typeof this.options.id !== 'undefined') {
        Router.navigate(this.url);
      }
    }
  },

  paginate: function paginate(e) {
    e.preventDefault();

    const options = {
      query: this.options.query,
      docType: this.options.docType,
      regVersion: this.options.regVersion,
      page: this.page + ($(e.target).hasClass('previous') ? -1 : 1),
    };

    MainEvents.trigger('search-results:open', null, options, 'search-results');
  },

  openResult: function openResult(e) {
        // TOC version retains the version the reg was loaded on whereas the content base section
        // changes to match the search results
        // page should reload if the TOC version doesn't match the searched version
    if (!this.resultsRegVersion || this.resultsRegVersion === $('nav#toc').attr('data-toc-version')) {
      e.preventDefault();
      const $resultLink = $(e.target);
      const pageType = this.options.docType === 'cfr' ? 'reg-section' : 'preamble-section';
      const options = {
        regVersion: $resultLink.data('linked-version'),
        scrollToId: $resultLink.data('linked-subsection'),
      };

      storage().dispatch(paneActiveEvt('table-of-contents'));
      MainEvents.trigger('section:open', $resultLink.data('linked-section'), options, pageType);
    }
  },
});

module.exports = SearchResultsView;
