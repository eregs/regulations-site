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
var comments = require('../../collections/comment-collection');

function getUploadUrl(file) {
  var prefix = window.APP_PREFIX || '/';
  return $.getJSON(
    prefix + 'comments/attachment',
    {size: file.size}
  ).then(function(resp) {
    return resp;
  });
}

function readFile(file) {
  var deferred = $.Deferred();
  var reader = new FileReader();
  reader.onload = function() {
    deferred.resolve(reader.result);
  };
  reader.readAsBinaryString(file);
  return deferred;
}

var CommentView = Backbone.View.extend({
  events: {
    'change input[type="file"]': 'addAttachment',
    'click .queue-item': 'clearAttachment',
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

    this.listenTo(CommentEvents, 'comment:target', this.target);

    this.setSection(options.section);
  },

  setSection: function(section, overwrite) {
    if (this.model) {
      this.stopListening(this.model);
    }
    if (section) {
      this.model = overwrite ?
        new CommentModel({id: section}) :
        comments.get(section) || new CommentModel({id: section});
      this.listenTo(this.model, 'destroy', this.setSection.bind(this, section, true));
      this.listenTo(this.model, 'change', this.render);
    }
    this.render();
  },

  target: function(options) {
    this.setSection(options.section);
    this.$context.empty();
    if (options.$parent) {
      this.$context.append(options.$parent);
    }
  },

  addQueueItem: function(key, name) {
    this.$queued.append(
      $('<div class="queue-item" data-key="' + key + '">' + name + '</div>')
    );
  },

  render: function() {
    var data = this.model ? this.model.toJSON() : {};
    this.editor.setContent(data.comment || '', 'markdown');
    this.$queued.empty();
    _.each(data.files || [], function(file) {
      this.addQueueItem(file.key, file.name);
    }.bind(this));
  },

  addAttachment: function(e) {
    var key;
    var file = e.target.files[0];
    if (!file) { return; }
    getUploadUrl(file).then(function(url) {
      key = url.key;
      return readFile(file).then(function(data) {
        return $.ajax({
          type: 'PUT',
          url: url.url,
          data: data,
          contentType: 'application/octet-stream',
          processData: false
        });
      });
    }).then(function(resp) {
      this.addQueueItem(key, file.name);
      $(e.target).val(null);
    }.bind(this));
  },

  clearAttachment: function(e) {
    var $target = $(e.target);
    var key = $target.data('key');
    $target.remove();
  },

  clear: function() {
    this.model.destroy();
  },

  save: function(e) {
    e.preventDefault();
    this.model.set('comment', this.editor.getContent('markdown'));
    this.model.set({
      comment: this.editor.getContent('markdown'),
      files: this.$queued.find('.queue-item').map(function(idx, elm) {
        var $elm = $(elm);
        return {
          key: $elm.data('key'),
          name: $elm.text()
        };
      }).get()
    });
    comments.add(this.model);
    this.model.save();
    this.$status.hide().html('Your comment was saved.').fadeIn();
  }
});

module.exports = CommentView;
