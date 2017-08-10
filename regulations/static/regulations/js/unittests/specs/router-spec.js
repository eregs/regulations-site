import { expect } from 'chai';
import jsdom from 'mocha-jsdom';
import sinon from 'sinon';

describe('RegRouter', () => {
  jsdom();
  let MainEvents;
  let RegRouter;
  let triggerStub;

  before(() => {
    MainEvents = require('../../source/events/main-events');
    RegRouter = require('../../source/router');
    triggerStub = sinon.stub(MainEvents, 'trigger');
    window.history.pushState = true;
  });

  describe('::loadSearchResults', () => {
    it('passes along the correct variables', () => {
      RegRouter.loadSearchResults(
        'aDocType', 'aReg', { q: 'terms here', version: 'aVersion' });
      expect(triggerStub).to.have.been.calledWith(
        'search-results:open',
        null,
        { query: 'terms here', regVersion: 'aVersion', docType: 'aDocType' },
        'search-results');
    });

    it('passes along the page, if present', () => {
      RegRouter.loadSearchResults(
        'aDocType',
        'aReg',
        { q: 'terms here', version: 'aVersion', page: '4', ignored: 'aaa' });
      expect(triggerStub).to.have.been.calledWith(
        'search-results:open',
        null,
        { query: 'terms here',
          regVersion: 'aVersion',
          docType: 'aDocType',
          page: '4' },
        'search-results');
    });
  });
});
