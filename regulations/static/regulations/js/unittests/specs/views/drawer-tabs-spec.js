import { createStore } from 'redux';
import { setStorage } from '../../../source/redux/storage';

var chai = require('chai');
var expect = chai.expect;
var jsdom = require('mocha-jsdom');


describe('DrawerTabsView', function() {
  jsdom();
  var $;
  const storage = createStore((state) => state, { activePane: 'table-of-contents' });

  describe('::initialize', function() {
    describe('with forceOpen', function() {
      var $fixture, view;

      beforeEach(function() {
        setStorage(storage);

        var DrawerTabsView = require('../../../source/views/drawer/drawer-tabs-view');
        $ = require('jquery');

        $fixture = $('<div id="fixutre"></div>');
        $fixture.append('<div class="toc-head"><a href="#" id="panel-link" class="toc-toggle panel-slide"></a></div>'

        ).appendTo('body');

        view = new DrawerTabsView({forceOpen: true});
      });

      afterEach(function() {
        view.remove();
        $fixture.remove();
        setStorage(null);
      });

      it('is in the open state', function() {
        expect(view).to.be.ok;
        expect(view.drawerState).to.eql('open');
        expect(view.$toggleArrow.attr('class')).to.match(/\bopen\b/);
      });
    });
  });
});
