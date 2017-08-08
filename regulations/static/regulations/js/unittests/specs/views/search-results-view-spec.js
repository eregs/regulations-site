import { expect } from 'chai';
import jsdom from 'mocha-jsdom';
import { createStore } from 'redux';

import { setStorage } from '../../../source/redux/storage';


describe('SearchResultsView', () => {
  jsdom();
  let Backbone;
  let $;
  let SearchResultsView;

  before(() => {
    Backbone = require('backbone');
    $ = require('jquery');
    Backbone.$ = $;
    SearchResultsView = require('../../../source/views/main/search-results-view');
    setStorage(createStore(state => state, {}));
  });

  describe('::initialize', () => {
    it('does not modify the id option, if given', () => {
      const view = new SearchResultsView(
        { id: 'some-id', docId: 'something-else' });
      expect(view.options.id).to.equal('some-id');
    });

    it('sets the id to the string version of the docId', () => {
      const view = new SearchResultsView({ docId: 1234 });
      expect(view.options.id).to.equal('1234');
    });

    it('sets the id to an empty string otherwise', () => {
      const view = new SearchResultsView({});
      expect(view.options.id).to.equal('');
    });
  });
});
