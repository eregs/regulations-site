var chai = require('chai');
var assert = chai.assert;
var jsdom = require('mocha-jsdom');

describe('CommentCollection', function() {
  jsdom();

  var commentComparator, CommentModel;

  before(function() {
    Backbone = require('backbone');
    $ = require('jquery');
    Backbone.$ = $;
    var comment_model = require('../../../source/models/comment-model');
    CommentModel = comment_model.CommentModel;
    commentComparator = comment_model.commentComparator;

  });

  it('sorts preamble before CFR', function() {
      var comment1 = new CommentModel({tocId: "toc-preamble-foo", preorder: [2]});
      var comment2 = new CommentModel({tocId: "toc-cfr-foo", preorder: [1]});
      assert.equal(-1, commentComparator(comment1, comment2));
  });

  it('sorts by preorder within preamble', function() {
      var comment1 = new CommentModel({tocId: "toc-preamble-bfoo", preorder: [0, 1]});
      var comment2 = new CommentModel({tocId: "toc-preamble-afoo", preorder: [0, 2]});
      assert.equal(-1, commentComparator(comment1, comment2));
  });

  it('sorts by preorder within CFR', function() {
      var comment1 = new CommentModel({tocId: "toc-CFR-bfoo", preorder: [0, 1]});
      var comment2 = new CommentModel({tocId: "toc-CFR-afoo", preorder: [0, 2]});
      assert.equal(-1, commentComparator(comment1, comment2));
  });

  it('handles preorder of different lengths when sorting by preorder', function() {
      var comment1 = new CommentModel({tocId: "toc-preamble-foo", preorder: [0, 3, 2, 1]});
      var comment2 = new CommentModel({tocId: "toc-preamble-foo", preorder: [0, 3, 3]});
      assert.equal(-1, commentComparator(comment1, comment2));
  });

  it('sorts by index magnitude (not lexical) when sorting by preorder ', function() {
      var comment1 = new CommentModel({tocId: "toc-preamble-foo", preorder: [0, 3]});
      var comment2 = new CommentModel({tocId: "toc-preamble-foo", preorder: [0, 20]});
      assert.equal(-1, commentComparator(comment1, comment2));
  });
});
