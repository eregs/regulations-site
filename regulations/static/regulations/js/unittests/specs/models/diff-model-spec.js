var expect = require('chai').expect;
var jsdom = require('mocha-jsdom');

describe('Diff Model:', function() {
  'use strict';

  var $, Backbone, DiffModel;

  jsdom();

  before(function (){
    Backbone = require('backbone');
    $ = require('jquery');
    Backbone.$ = $;
    DiffModel = require('../../../source/models/diff-model');
  });

  it('getAJAXUrl returns the correct URL endpoint with /diff supplemental path', function() {
    var options = {
      id: '1005-2',
      baseVersion: '2014-20681',
      newerVersion: '2015-18261',
      fromVersion: '2015-18261'
    };

    window.APP_PREFIX = '/eregulations/';
    expect(
      DiffModel.getAJAXUrl(null, options)
    ).to.equal(
      '/eregulations/partial/diff/1005-2/2014-20681/2015-18261?from_version=2015-18261'
    );

    window.APP_PREFIX = '/';
    expect(
      DiffModel.getAJAXUrl(null, options)
    ).to.equal(
      '/partial/diff/1005-2/2014-20681/2015-18261?from_version=2015-18261'
    );
  });
});
