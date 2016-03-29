'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var edit = require('prosemirror/dist/edit');
require('prosemirror/dist/menu/tooltipmenu');
require('prosemirror/dist/markdown');

var CommentModel = require('../../models/comment-model');
var CommentEvents = require('../../events/comment-events');
var AttachmentView = require('../../views/comment/attachment-view');
var comments = require('../../collections/comment-collection');

function getUploadUrl(file) {
  var prefix = window.APP_PREFIX || '/';
  return $.getJSON(
    prefix + 'comments/attachment',
    {size: file.size, type: file.type || 'application/octet-stream'}
  ).then(function(resp) {
    return resp;
  });
}

var CommentView = Backbone.View.extend({
  events: {
    'change input[type="file"]': 'addAttachment',
    'click .comment-clear': 'clear',
    'submit form': 'save'
  },

  initialize: function(options) {
    this.$context = this.$el.find('.comment-context');
    this.$container = this.$el.find('.editor-container');
    this.$queued = this.$el.find('.queued');
    this.$status = this.$el.find('.status');

    this.editor = new edit.ProseMirror({
      tooltipMenu: true,
      place: this.$container.get(0),
      docFormat: 'markdown',
      doc: ''
    });

    this.attachmentViews = [];

    this.listenTo(CommentEvents, 'comment:target', this.target);
    this.listenTo(CommentEvents, 'attachment:remove', this.clearAttachment);

    this.setSection(options.section);
  },

  setSection: function(section, blank) {
    if (this.model) {
      this.stopListening(this.model);
    }
    this.model = blank ?
      new CommentModel({id: section}) :
      comments.get(section) || new CommentModel({id: section});
    this.listenTo(this.model, 'destroy', this.setSection.bind(this, section, true));
    this.render();
  },

  target: function(options) {
    this.setSection(options.section);
    this.$context.empty();
    if (options.$parent) {
      this.$context.append(options.$parent);
    }
  },

  render: function() {
    this.editor.setContent(this.model.get('comment'), 'markdown');
    this.$queued.empty();
    this.attachmentViews = this.model.get('files').map(function(file) {
      return new AttachmentView(_.extend({$parent: this.$queued}, file));
    }.bind(this));
  },

  addAttachment: function(e) {
    var file = e.target.files[0];
    if (!file) { return; }
    getUploadUrl(file).then(function(url) {
      var xhr = new XMLHttpRequest();
      this.attachmentViews.push(
        new AttachmentView({
          $parent: this.$queued,
          name: file.name,
          size: file.size,
          key: url.key,
          xhr: xhr
        })
      );
      xhr.open('PUT', url.url);
      xhr.setRequestHeader('Content-Type', file.type || 'application/octet-stream');
      xhr.send(file);
    }.bind(this));
  },

  clearAttachment: function(key) {
    var index = _.findIndex(this.attachmentViews, function(view) {
      return view.options.key === key;
    });
    this.attachmentViews.splice(index, 1)[0].remove();
  },

  clear: function() {
    this.model.destroy();
  },

  save: function(e) {
    e.preventDefault();
    this.model.set({
      comment: this.editor.getContent('markdown'),
      files: _.map(this.attachmentViews, function(view) {
        return {
          key: view.options.key,
          name: view.options.name,
          size: view.options.size
        };
      })
    });
    comments.add(this.model);
    this.model.save();
    this.$status.hide().html('Your comment was saved.').fadeIn();
  }
});

module.exports = CommentView;
