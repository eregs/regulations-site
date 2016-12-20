var chai = require('chai');
var expect = chai.expect;
var jsdom = require('mocha-jsdom');
var localStorage = require('node-localstorage');

var storage = new localStorage.LocalStorage('.');

describe('CommentConfirmView', function() {
  jsdom();

  var $el, comments, CommentConfirmView, CommentModel;
  var Backbone, $;

  before(function() {
    Backbone = require('backbone');
    $ = require('jquery');
    Backbone.$ = $;
    global.localStorage = window.localStorage = storage;
    comments = require('../../../source/collections/comment-collection');
    CommentModel = require('../../../source/models/comment-model').CommentModel;
    CommentConfirmView = require('../../../source/views/comment/comment-confirm-view');
  });

  beforeEach(function() {
    comments.models.forEach(function(comment) {
      comment.destroy();
    });
    var models = [
      new CommentModel({docId: 'foo'}),
      new CommentModel({docId: 'bar'})
    ];
    comments.add(models);
    models.forEach(function(model) { model.save(); });
  });

  afterEach(function() {
    comments.models.forEach(function(comment) {
      comment.destroy();
    });
  });

  it('clears comments when metadata is defined', function() {
    var $el = $('<div id="confirm" data-doc-id="foo" data-metadata-url="https://s3.amazonaws.con/bucket/meta"></div>');
    $('body').empty().append($el);
    var view = new CommentConfirmView({id: 'confirm'});
    expect(comments.filter('foo').length).to.equal(0);
    expect(comments.filter('bar').length).to.equal(1);
  });

  it('does not clear comments when metadata is undefined', function() {
    var $el = $('<div id="confirm" data-doc-id="foo" data-metadata-url></div>');
    $('body').empty().append($el);
    var view = new CommentConfirmView({id: 'confirm'});
    expect(comments.filter('foo').length).to.equal(1);
    expect(comments.filter('bar').length).to.equal(1);
  });
});
