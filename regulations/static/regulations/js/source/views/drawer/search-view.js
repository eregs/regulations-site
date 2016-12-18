

const $ = require('jquery');
const Backbone = require('backbone');
const Router = require('../../router');
const MainEvents = require('../../events/main-events');

Backbone.$ = $;

const SearchView = Backbone.View.extend({
  el: '#search',

  events: {
    submit: 'openSearchResults',
  },

  initialize: function initialize() {
        // if the browser doesn't support pushState, don't
        // trigger click events for links
    if (Router.hasPushState === false) {
      this.events = {};
    }
  },

  openSearchResults: function openSearchResults(e) {
    sessionStorage.setItem('drawerDefault', 'search');

    e.preventDefault();
    const $form = $(e.target);
    const options = {
      docType: $form.data('doc-type'),
      query: $form.find('input[name="q"]').val(),
      searchVersion: $form.find('select[name=version]').val(),
    };

    MainEvents.trigger('search-results:open', null, options, 'search-results');
  },

});

module.exports = SearchView;
