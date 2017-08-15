var chai = require('chai');
var expect = chai.expect;
var jsdom = require('mocha-jsdom');

let $;    // Must be loaded after the jsdom

// jsdom doesn't support jQuery's latest revision of :visible
function isVisible($el) {
  const elHidden = $el.css('display') === 'none';
  const parentHidden = $el.parents().filter(
    (idx, p) => $(p).css('display') === 'none').length > 0;
  return !elHidden && !parentHidden;
}

describe('starsHelpers.inline', function() {
  jsdom();
  var starsHelpers, $li;

  before(function() {
    $ = require('jquery');
    starsHelpers = require('../../../source/views/main/stars-helpers');
    $li = $(
      '<li><p>' +
      '<span class="collapsed-marker">b.</span>' +
      '<span class="paragraph-text">Remainder of the text</span>' +
      '</p></li>');
  });

  it('does not hide the marker, but does hide the intro text', function() {
    starsHelpers.inline($li);
    expect(isVisible($li.find('.collapsed-marker'))).to.be.true;
    expect(isVisible($li.find('.paragraph-text'))).to.be.false;
  });
  it('generates an expander which reverses the hiding', function() {
    var $expander = starsHelpers.inline($li);
    expect($li.find($expander)).to.be.ok;

    $expander.click();
    expect(isVisible($li.find('.collapsed-marker'))).to.be.true;
    expect(isVisible($li.find('.paragraph-text'))).to.be.true;
    expect($li.find($expander).length).to.equal(0);
  });
  it('unsets and resets the "collapsed" class', function() {
    var $expander = starsHelpers.inline($li);
    expect($li.find('.collapsed')).not.to.be.truthy;

    $expander.click();
    expect($li.find('.collapsed')).to.be.truthy;
  });
});

describe('starsHelpers.full', function() {
  jsdom();
  var starsHelpers, $li;

  before(function() {
    $ = require('jquery');
    starsHelpers = require('../../../source/views/main/stars-helpers');
    $li = $(
      '<li><p>' +
      '<span class="collapsed-marker">b.</span>' +
      '<span class="paragraph-text">Remainder of the text</span>' +
      '</p></li>');
  });

  it('hides everything within the li if no expander is provided', function() {
    starsHelpers.full($li, null);
    expect(isVisible($li)).to.be.true;
    expect(isVisible($li.find('.collapsed-marker'))).to.be.false;
    expect(isVisible($li.find('.paragraph-text'))).to.be.false;
  });
  it('if no expander is provided, a new one is generated', function() {
    var $expander = starsHelpers.full($li, null);
    expect($li.find($expander)).to.be.ok;

    $expander.click();
    expect(isVisible($li.find('.collapsed-marker'))).to.be.true;
    expect(isVisible($li.find('.paragraph-text'))).to.be.true;
    expect($li.find($expander).length).to.equal(0);
  });
  it('reuses an existing expander, if provided and hides the li', function() {
    var $expander = $('<button>');
    starsHelpers.full($li, $expander);

    expect(isVisible($li)).to.be.false;
    expect(isVisible($li.find('.collapsed-marker'))).to.be.false;
    expect(isVisible($li.find('.paragraph-text'))).to.be.false;
    $expander.click();
    expect(isVisible($li)).to.be.true;
    expect(isVisible($li.find('.collapsed-marker'))).to.be.true;
    expect(isVisible($li.find('.paragraph-text'))).to.be.true;
  });
});
