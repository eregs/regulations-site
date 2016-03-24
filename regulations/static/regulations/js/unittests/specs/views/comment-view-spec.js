var chai = require('chai');
var expect = chai.expect;
var sinon = require('sinon');
var jsdom = require('mocha-jsdom');
var localStorage = require('node-localstorage');

var storage = new localStorage.LocalStorage('.');

describe('CommentView', function() {
  jsdom();

  var $el, commentView, CommentView, CommentEvents;

  before(function() {
    Backbone = require('backbone');
    $ = require('jquery');
    Backbone.$ = $;
    CommentView = require('../../../source/views/comment-view');
    CommentEvents = require('../../../source/events/comment-events');
    window.localStorage = storage;
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
    commentView = new CommentView({el: $el});
  });

  it('setSection()', function() {
    commentView.setSection('2016_02749-III-B');
    expect(commentView.section).to.equal('2016_02749-III-B');
    expect(commentView.key).to.equal('comment:2016_02749-III-B');
  });

  it('fetches from localstorage', function() {
    var payload = {
      comment: 'like',
      files: [
        {key: '6bc649', name: 'attachment.txt'}
      ],
    };
    commentView.setSection('2016_02479');
    window.localStorage.setItem('comment:2016_02479', JSON.stringify(payload));
    expect(commentView.getStorage()).to.deep.equal(payload);
  });

  it('writes to localstorage', function() {
    commentView.setSection('2016_02479');
    sinon.stub(commentView.editor, 'getContent').returns('dislike');
    commentView.addQueueItem('6bc649', 'attachment.txt');
    commentView.setStorage();
    var payload = {
      comment: 'dislike',
      files: [
        {key: '6bc649', name: 'attachment.txt'}
      ],
    };
    expect(commentView.getStorage()).to.deep.equal(payload);
  });

  it('adds a queue item', function() {
    commentView.addQueueItem('6bc649', 'attachment.txt');
    var $item = commentView.$queued.find('.queue-item');
    expect($item.length).to.equal(1);
    expect($item.data('key')).to.equal('6bc649');
    expect($item.text()).to.equal('attachment.txt');
  });

  it('loads state from localstorage', function() {
    var payload = {
      comment: 'like',
      files: [
        {key: '6bc649', name: 'attachment.txt'}
      ],
    };
    commentView.setSection('2016_02479');
    window.localStorage.setItem('comment:2016_02479', JSON.stringify(payload));
    sinon.stub(commentView.editor, 'setContent');
    commentView.load();
    expect(commentView.editor.setContent).to.have.been.calledWith('like', 'markdown');
    var $item = commentView.$queued.find('.queue-item');
    expect($item.length).to.equal(1);
    expect($item.data('key')).to.equal('6bc649');
    expect($item.text()).to.equal('attachment.txt');
  });

  it('clears', function() {
    commentView.setSection('2016_02479');
    sinon.stub(commentView.editor, 'setContent');
    sinon.stub(commentView.editor, 'getContent').returns('dislike');
    commentView.addQueueItem('6bc649', 'attachment.txt');
    commentView.setStorage();
    commentView.clear();
    expect(commentView.getStorage()).to.deep.equal({});
    expect(commentView.$queued.find('.queue-item').length).to.equal(0);
  });
});
