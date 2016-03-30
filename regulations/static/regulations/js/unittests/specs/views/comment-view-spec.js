var chai = require('chai');
var expect = chai.expect;
var sinon = require('sinon');
var jsdom = require('mocha-jsdom');
var localStorage = require('node-localstorage');

var storage = new localStorage.LocalStorage('.');

describe('CommentView', function() {
  jsdom();

  var $el, comments, commentView, CommentView, AttachmentView, CommentEvents, edit;

  before(function() {
    Backbone = require('backbone');
    $ = require('jquery');
    Backbone.$ = $;
    edit = require('prosemirror/dist/edit');
    global.localStorage = window.localStorage = storage;
    comments = require('../../../source/collections/comment-collection');
    CommentEvents = require('../../../source/events/comment-events');
    CommentView = require('../../../source/views/comment/comment-view');
    AttachmentView = require('../../../source/views/comment/attachment-view');
  });

  beforeEach(function() {
    $el = $(
      '<div class="comment">' +
        '<form>' +
          '<div class="editor-container"></div>' +
          '<div class="comment-attachments"></div>' +
          '<input type="file">' +
          '<button type="submit">Save</button>' +
          '<div class="comment-clear">Clear</div>' +
          '<div class="status"></div>' +
        '</form>' +
      '</div>'
    );
    var $template = $(
      '<script id="comment-attachment-template" type="text/template">' +
        '<div></div>' +
      '</script>'
    );
    var $body = $(document.body)
      .empty()
      .append($el)
      .append($template);
    sinon.stub(edit.ProseMirror.prototype, 'getContent');
    sinon.stub(edit.ProseMirror.prototype, 'setContent');
    commentView = new CommentView({el: $el});
    comments.reset();
  });

  afterEach(function() {
    edit.ProseMirror.prototype.getContent.restore();
    edit.ProseMirror.prototype.setContent.restore();
  });

  it('removes an attachment', function() {
    commentView.attachmentViews.push(
      new AttachmentView({
        $parent: commentView.$attachments,
        key: '6bc649',
        name: 'attachment.txt',
        size: 1234
      })
    );
    commentView.clearAttachment('6bc649');
    expect(commentView.attachmentViews.length).to.equal(0);
  });

  it('reads from models', function() {
    comments.add({
      id: '2016_02749',
      comment: 'like',
      files: [
        {key: '6bc649', name: 'attachment.txt', size: 1234}
      ],
    });
    commentView.setSection('2016_02749');
    expect(commentView.attachmentViews.length).to.equal(1);
    var attachment = commentView.attachmentViews[0];
    expect(attachment.options.key).to.equal('6bc649');
    expect(commentView.editor.setContent).to.have.been.calledWith('like', 'markdown');
  });

  it('writes to models', function() {
    commentView.setSection('2016_02479');
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
    expect(commentView.$attachments.find('.queue-item').length).to.equal(0);
  });
});
