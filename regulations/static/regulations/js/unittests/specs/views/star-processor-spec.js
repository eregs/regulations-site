var chai = require('chai');
var expect = chai.expect;
var jsdom = require('mocha-jsdom');

describe('StarProcessor.inline', function() {
  jsdom();
  var StarProcessor;

  before(function() {
    $ = require('jquery');
    StarProcessor = require('../../../source/views/main/star-processor');
  });

  it('does not hide the marker, but does hide the intro text', function() {
    var $li = $(
      '<li><p>' +
      '<span class="collapsed-marker">b.</span>' +
      '<span class="paragraph-text">Remainder of the text</span>' +
      '</p></li>');
    StarProcessor.inline($li);
    expect($li.find('.collapsed-marker').is(':visible')).to.be.true;
    expect($li.find('.paragraph-text').is(':visible')).to.be.false;
  });
  it('generates an expander which reverses the hiding', function() {
    var $li = $(
      '<li><p>' +
      '<span class="collapsed-marker">b.</span>' +
      '<span class="paragraph-text">Remainder of the text</span>' +
      '</p></li>');
    var $expander = StarProcessor.inline($li);
    expect($li.find($expander)).to.be.ok;

    $expander.click();
    expect($li.find('.collapsed-marker').is(':visible')).to.be.true;
    expect($li.find('.paragraph-text').is(':visible')).to.be.true;
    expect($li.find($expander).length).to.equal(0);
  });
  it('unsets and resets the "collapsed" class', function() {
    var $li = $(
      '<li><p class="collapsed">' +
      '<span class="collapsed-marker">b.</span>' +
      '<span class="paragraph-text">Remainder of the text</span>' +
      '</p></li>');
    var $expander = StarProcessor.inline($li);
    expect($li.find('.collapsed')).not.to.be.truthy;

    $expander.click();
    expect($li.find('.collapsed')).to.be.truthy;
  });
});

describe('StarProcessor.full', function() {
  jsdom();
  var StarProcessor;

  before(function() {
    $ = require('jquery');
    StarProcessor = require('../../../source/views/main/star-processor');
  });

  it('hides everything', function() {
    var $li = $(
      '<li><p>' +
      '<span class="collapsed-marker">b.</span>' +
      '<span class="paragraph-text">Remainder of the text</span>' +
      '</p></li>');
    StarProcessor.full($li, null);
    expect($li.find('.collapsed-marker').is(':visible')).to.be.false;
    expect($li.find('.paragraph-text').is(':visible')).to.be.false;
  });
  it('if no expander is provided, a new one is generated', function() {
    var $li = $(
      '<li><p>' +
      '<span class="collapsed-marker">b.</span>' +
      '<span class="paragraph-text">Remainder of the text</span>' +
      '</p></li>');
    var $expander = StarProcessor.full($li, null);
    expect($li.find($expander)).to.be.ok;

    $expander.click();
    expect($li.find('.collapsed-marker').is(':visible')).to.be.true;
    expect($li.find('.paragraph-text').is(':visible')).to.be.true;
    expect($li.find($expander).length).to.equal(0);
  });
  it('reuses an existing expander, if provided', function() {
    var $li = $(
      '<li><p class="collapsed">' +
      '<span class="collapsed-marker">b.</span>' +
      '<span class="paragraph-text">Remainder of the text</span>' +
      '</p></li>');
    var $expander = $('<button>');
    StarProcessor.full($li, $expander);

    expect($li.find('.collapsed-marker').is(':visible')).to.be.false;
    expect($li.find('.paragraph-text').is(':visible')).to.be.false;
    $expander.click();
    expect($li.find('.collapsed-marker').is(':visible')).to.be.true;
    expect($li.find('.paragraph-text').is(':visible')).to.be.true;
  });
});
