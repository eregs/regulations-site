var chai = require('chai');
var expect = chai.expect;
var jsdom = require('mocha-jsdom');

var helpers = require('../spec-helpers');


describe('DrawerTabsView', function() {
  jsdom();

  describe('::initialize', function() {
    describe('with forceOpen', function() {
      var $fixture, view;

      beforeEach(function() {
        var DrawerTabsView = require('../../../source/views/drawer/drawer-tabs-view');

        $fixture = $('<div id="fixutre"></div>');
        $fixture.append('<div class="toc-head"><a href="#" id="panel-link" class="toc-toggle panel-slide"></a></div>'

        ).appendTo('body');

        view = new DrawerTabsView({forceOpen: true});
      });

      afterEach(function() {
        view.remove();
        $fixture.remove();
      });

      it('is in the open state', function() {
        expect(view).to.be.ok;
        expect(view.drawerState).to.eql('open');
        expect(view.$toggleArrow.attr('class')).to.match(/\bopen\b/);
      });
    });
  });
});
