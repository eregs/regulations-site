var chai = require('chai');
var assert = chai.assert;
var jsdom = require('mocha-jsdom');

describe('CommentCollection', function() {
  jsdom();

  var commentComparator, CommentModel;
  var Backbone, $;

  before(function() {
    Backbone = require('backbone');
    $ = require('jquery');
    Backbone.$ = $;
    var commentModel = require('../../../source/models/comment-model');
    CommentModel = commentModel.CommentModel;
    commentComparator = commentModel.commentComparator;

  });


  it('sorts by indexes', function() {
      var comment1 = new CommentModel({indexes: [0, 1]});
      var comment2 = new CommentModel({indexes: [0, 2]});
      assert.equal(-1, commentComparator(comment1, comment2));
  });

  it('handles indexes of different lengths', function() {
      var comment1 = new CommentModel({indexes: [0, 3, 2, 1]});
      var comment2 = new CommentModel({indexes: [0, 3, 3]});
      assert.equal(-1, commentComparator(comment1, comment2));
  });

  it('sorts by index magnitude as opposed to lexical sorting', function() {
      var comment1 = new CommentModel({indexes: [0, 3]});
      var comment2 = new CommentModel({indexes: [0, 20]});
      assert.equal(-1, commentComparator(comment1, comment2));
  });
});
