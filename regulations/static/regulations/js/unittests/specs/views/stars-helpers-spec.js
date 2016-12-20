var chai = require('chai');
var expect = chai.expect;
var jsdom = require('mocha-jsdom');

describe('starsHelpers.inline', function() {
  jsdom();
  var starsHelpers, $;

  before(function() {
    $ = require('jquery');
    starsHelpers = require('../../../source/views/main/stars-helpers');
  });

  it('does not hide the marker, but does hide the intro text', function() {
    var $li = $(
      '<li><p>' +
      '<span class="collapsed-marker">b.</span>' +
      '<span class="paragraph-text">Remainder of the text</span>' +
      '</p></li>');
    starsHelpers.inline($li);
    expect($li.find('.collapsed-marker').is(':visible')).to.be.true;
    expect($li.find('.paragraph-text').is(':visible')).to.be.false;
  });
  it('generates an expander which reverses the hiding', function() {
    var $li = $(
      '<li><p>' +
      '<span class="collapsed-marker">b.</span>' +
      '<span class="paragraph-text">Remainder of the text</span>' +
      '</p></li>');
    var $expander = starsHelpers.inline($li);
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
    var $expander = starsHelpers.inline($li);
    expect($li.find('.collapsed')).not.to.be.truthy;

    $expander.click();
    expect($li.find('.collapsed')).to.be.truthy;
  });
});

describe('starsHelpers.full', function() {
  jsdom();
  var starsHelpers, $;

  before(function() {
    $ = require('jquery');
    starsHelpers = require('../../../source/views/main/stars-helpers');
  });

  it('hides everything within the li if no expander is provided', function() {
    var $li = $(
      '<li><p>' +
      '<span class="collapsed-marker">b.</span>' +
      '<span class="paragraph-text">Remainder of the text</span>' +
      '</p></li>');
    starsHelpers.full($li, null);
    expect($li.is(':visible')).to.be.true;
    expect($li.find('.collapsed-marker').is(':visible')).to.be.false;
    expect($li.find('.paragraph-text').is(':visible')).to.be.false;
  });
  it('if no expander is provided, a new one is generated', function() {
    var $li = $(
      '<li><p>' +
      '<span class="collapsed-marker">b.</span>' +
      '<span class="paragraph-text">Remainder of the text</span>' +
      '</p></li>');
    var $expander = starsHelpers.full($li, null);
    expect($li.find($expander)).to.be.ok;

    $expander.click();
    expect($li.find('.collapsed-marker').is(':visible')).to.be.true;
    expect($li.find('.paragraph-text').is(':visible')).to.be.true;
    expect($li.find($expander).length).to.equal(0);
  });
  it('reuses an existing expander, if provided and hides the li', function() {
    var $li = $(
      '<li><p class="collapsed">' +
      '<span class="collapsed-marker">b.</span>' +
      '<span class="paragraph-text">Remainder of the text</span>' +
      '</p></li>');
    var $expander = $('<button>');
    starsHelpers.full($li, $expander);

    expect($li.is(':visible')).to.be.false;
    expect($li.find('.collapsed-marker').is(':visible')).to.be.false;
    expect($li.find('.paragraph-text').is(':visible')).to.be.false;
    $expander.click();
    expect($li.is(':visible')).to.be.true;
    expect($li.find('.collapsed-marker').is(':visible')).to.be.true;
    expect($li.find('.paragraph-text').is(':visible')).to.be.true;
  });
});
