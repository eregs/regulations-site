'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var edit = require('prosemirror/dist/edit');
require('prosemirror/dist/menu/tooltipmenu');
require('prosemirror/dist/markdown');

function getUploadUrl() {
  var prefix = window.APP_PREFIX || '/';
  return $.getJSON(prefix + 'comments/attachment').then(function(resp) {
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
    'click .toggle': 'toggle',
    'change input[type="file"]': 'addAttachment',
    'click .queue-item': 'clearAttachment',
    'submit form': 'save'
  },

  initialize: function(options) {
    this.$content = this.$el.find('.comment');
    this.$toggle = this.$el.find('.toggle');
    this.$container = this.$el.find('.editor-container');
    this.$queued = this.$el.find('.queued');
    this.section = this.$el.data('section');
    this.key = 'comment:' + this.section;

    if (options.hide) {
      this.$content.hide();
    }
    this.editor = new edit.ProseMirror({
      tooltipMenu: true,
      place: this.$container.get(0),
      docFormat: 'markdown',
      doc: ''
    });
    this.load();
  },

  render: function() {},

  toggle: function() {
    this.$content.fadeToggle();

    if (this.$content.is(':visible')) {
      $('html, body').animate({
        scrollTop: this.$container.offset().top
      }, 2000);
    }
  },

  getStorage: function() {
    return JSON.parse(window.localStorage.getItem(this.key) || '{}');
  },

  setStorage: function() {
    var payload = {
      // comment: this.$comment.val(),
      comment: this.editor.getContent('markdown'),
      files: this.$queued.find('.queue-item').map(function(idx, elm) {
        var $elm = $(elm);
        return {
          key: $elm.data('key'),
          name: $elm.text()
        };
      }).get()
    };
    window.localStorage.setItem(this.key, JSON.stringify(payload));
  },

  addQueueItem: function(key, name) {
    this.$queued.append(
      $('<div class="queue-item" data-key="' + key + '">' + name + '</div>')
    );
  },

  load: function() {
    var payload = this.getStorage();
    if (payload.comment) {
      this.editor.setContent(payload.comment, 'markdown');
    }
    _.each(payload.files || [], function(file) {
      this.addQueueItem(file.key, file.name);
    }.bind(this));
  },

  addAttachment: function(e) {
    var file = e.target.files[0];
    if (!file) { return; }
    $.when(getUploadUrl(), readFile(file)).done(function(url, data) {
      $.ajax({
        type: 'PUT',
        url: url.url,
        data: data,
        contentType: 'application/octet-stream',
        processData: false
      }).done(function(resp) {
        this.addQueueItem(url.key, file.name);
        $(e.target).val(null);
      }.bind(this));
    }.bind(this));
  },

  clearAttachment: function(e) {
    var $target = $(e.target);
    var key = $target.data('key');
    var payload = this.getStorage();
    $target.remove();
  },

  save: function(e) {
    e.preventDefault();
    this.setStorage();
  }
});

module.exports = CommentView;
