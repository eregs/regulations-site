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

  it('sorts by tocId', function() {
      var comment1 = new CommentModel({tocId: "TocId 1", indexes: []});
      var comment2 = new CommentModel({tocId: "TocId 2", indexes: []});
      assert.equal(-1, commentComparator(comment1, comment2));
  });

  it('sorts by indexes when tocIds are equal', function() {
      var comment1 = new CommentModel({tocId: "TocId", indexes: [0, 1]});
      var comment2 = new CommentModel({tocId: "TocId", indexes: [0, 2]});
      assert.equal(-1, commentComparator(comment1, comment2));
  });

  it('sorts by indexes of different lengths when tocIds are equal', function() {
      var comment1 = new CommentModel({tocId: "TocId", indexes: [0, 3, 2, 1]});
      var comment2 = new CommentModel({tocId: "TocId", indexes: [0, 3, 3]});
      assert.equal(-1, commentComparator(comment1, comment2));
  });
});