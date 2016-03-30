var chai = require('chai');
var expect = chai.expect;
var sinon = require('sinon');
var jsdom = require('mocha-jsdom');
var localStorage = require('node-localstorage');

var storage = new localStorage.LocalStorage('.');

describe('CommentView', function() {
  jsdom();

  var $el, comments, commentView, CommentView, CommentEvents, edit;

  before(function() {
    Backbone = require('backbone');
    $ = require('jquery');
    Backbone.$ = $;
    edit = require('prosemirror/dist/edit');
    global.localStorage = window.localStorage = storage;
    comments = require('../../../source/collections/comment-collection');
    CommentEvents = require('../../../source/events/comment-events');
    CommentView = require('../../../source/views/comment/comment-view');
  });

  beforeEach(function() {
    $el = $(
      '<div class="comment">' +
        '<form>' +
          '<div class="editor-container"></div>' +
          '<div class="queued"></div>' +
          '<input type="file">' +
          '<button type="submit">Save</button>' +
          '<div class="comment-clear">Clear</div>' +
          '<div class="status"></div>' +
        '</form>' +
      '</div>'
    );
    $(document.body).empty().append($el);
    sinon.stub(edit.ProseMirror.prototype, 'getContent');
    sinon.stub(edit.ProseMirror.prototype, 'setContent');
    commentView = new CommentView({el: $el});
    comments.reset();
  });

  afterEach(function() {
    edit.ProseMirror.prototype.getContent.restore();
    edit.ProseMirror.prototype.setContent.restore();
  });

  it('adds a queue item', function() {
    commentView.addQueueItem('6bc649', 'attachment.txt');
    var $item = commentView.$queued.find('.queue-item');
    expect($item.length).to.equal(1);
    expect($item.data('key')).to.equal('6bc649');
    expect($item.text()).to.equal('attachment.txt');
  });

  it('removes a queue item', function() {
    commentView.addQueueItem('6bc649', 'attachment.txt');
    commentView.clearAttachment({target: commentView.$queued.find('.queue-item')});
    var $item = commentView.$queued.find('.queue-item');
    expect($item.length).to.equal(0);
  });

  it('reads from models', function() {
    comments.add({
      id: '2016_02749',
      comment: 'like',
      files: [
        {key: '6bc649', name: 'attachment.txt'}
      ],
    });
    commentView.setSection('2016_02749');
    var $item = commentView.$queued.find('.queue-item');
    expect($item.length).to.equal(1);
    expect($item.data('key')).to.equal('6bc649');
    expect(commentView.editor.setContent).to.have.been.calledWith('like', 'markdown');
  });

  it('writes to models', function() {
    commentView.setSection('2016_02479');
    commentView.addQueueItem('6bc649', 'attachment.txt');
    expect(comments.get('2016_02479')).to.be.falsy;
    commentView.save({preventDefault: function() {}});
    expect(comments.get('2016_02479')).to.be.truthy;
  });

  it('clears', function() {
    comments.add({
      id: '2016_02749',
      comment: 'like',
      files: [
        {key: '6bc649', name: 'attachment.txt'}
      ],
    });
    commentView.setSection('2016_02479');
    commentView.save({preventDefault: function() {}});
    commentView.clear();
    expect(comments.get('2016_02479')).to.be.falsy;
    expect(commentView.editor.setContent).to.have.been.calledWith('', 'markdown');
    expect(commentView.$queued.find('.queue-item').length).to.equal(0);
  });
});
