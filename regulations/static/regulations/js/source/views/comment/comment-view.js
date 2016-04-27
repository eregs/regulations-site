'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
var filesize = require('filesize');
Backbone.$ = $;

var edit = require('prosemirror/dist/edit');
require('prosemirror/dist/menu/tooltipmenu');
require('prosemirror/dist/markdown');

var MainEvents = require('../../events/main-events');
var DrawerEvents = require('../../events/drawer-events');
var CommentModel = require('../../models/comment-model');
var CommentEvents = require('../../events/comment-events');
var AttachmentView = require('../../views/comment/attachment-view');
var comments = require('../../collections/comment-collection');
var helpers = require('../../helpers');

/**
 * Get a presigned upload URL.
 * The file extension (from the name) and size are validated
 * and the uploadURL is constrained by the file name and size.
 *
 * @param file {File} File to upload
 */
function getUploadUrl(file) {
  return $.getJSON(
    window.APP_PREFIX + 'comments/attachment',
    {size: file.size, name: file.name, type: file.type || 'application/octet-stream'}
  ).then(function(resp) {
    return resp;
  });
}

var CommentView = Backbone.View.extend({
  events: {
    'change input[type="file"]': 'addAttachments',
    'dragenter input[type="file"]': 'highlightDropzone',
    'dragleave input[type="file"]': 'unhighlightDropzone',
    'click .comment-header': 'openComment',
    'submit form': 'save'
  },

  initialize: function(options) {
    this.options = options;

    this.$context = this.$el.find('.comment-context');
    this.$header = this.$el.find('.comment-header');
    this.$container = this.$el.find('.editor-container');
    this.$input = this.$el.find('input[type="file"]');
    this.$attachments = this.$el.find('.comment-attachments');
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

    this.setSection(options.section, options.tocId, options.label);
  },

  setSection: function(section, tocId, label, blank) {
    if (this.model) {
      this.stopListening(this.model);
    }
    var options = {id: section, tocId: tocId, label: label, docId: this.options.docId};
    this.model = blank ?
      new CommentModel(options) :
      comments.get(section) || new CommentModel(options);
    this.listenTo(this.model, 'destroy', this.setSection.bind(this, section, tocId, label, true));
    this.render();
  },

  target: function(options) {
    this.setSection(options.section, options.tocId, options.label);
    this.$context.empty();
    if (options.$parent) {
      var label = options.label;
      var parsed = helpers.parsePreambleId(options.section);
      var href = window.APP_PREFIX + parsed.path.join('/') + '#' + parsed.hash;
      // Splice section label and context title, if present
      // TODO: Build this upstream
      var $sectionHeader = options.$parent.find('.node:first :header, .section-title:header');
      if ($sectionHeader.length) {
        label = [label, $sectionHeader.text().split('. ').slice(1)].join('. ');
        $sectionHeader.remove();
      }
      this.$header.html('<a href="' + href + '">' + label + '</a>');
      this.$context.append(options.$parent);
    }
  },

  openComment: function(e) {
    e.preventDefault();
    var options = {
      section: this.model.get('id'),
      tocId: this.model.get('tocId'),
      label: this.model.get('label')
    };
    // TODO: Push this logic into `PreambleView`
    var type = options.section.split('-')[1];
    DrawerEvents.trigger('section:open', options.tocId);
    DrawerEvents.trigger('pane:change', type === 'preamble' ? 'table-of-contents' : 'table-of-contents-secondary');
    MainEvents.trigger('section:open', options.section, options, 'preamble-section');
  },

  render: function() {
    this.editor.setContent(this.model.get('comment'), 'markdown');
    this.$attachments.empty();
    this.attachmentViews = this.model.get('files').map(function(file) {
      return new AttachmentView(_.extend({$parent: this.$attachments}, file));
    }.bind(this));
  },

  highlightDropzone: function() {
    this.$input.addClass('highlight');
  },

  unhighlightDropzone: function() {
    this.$input.removeClass('highlight');
  },

  addAttachments: function(e) {
    _.each(e.target.files, function(file) {
      this.addAttachment(file);
    }.bind(this));
    this.$input.val(null);
    this.unhighlightDropzone();
  },

  /**
   * Upload an attachment. Request a signed upload URL, PUT the file via
   * XMLHttpRequest, and pass the XHR to AttachmentView for rendering.
   *
   * @param {File} file File to upload
   */
  addAttachment: function(file) {
    getUploadUrl(file).then(function(resp) {
      var xhr = new XMLHttpRequest();
      this.attachmentViews.push(
        new AttachmentView({
          $parent: this.$attachments,
          previewUrl: resp.urls.get,
          name: file.name,
          size: filesize(file.size),
          key: resp.key,
          xhr: xhr
        })
      );
      xhr.open('PUT', resp.urls.put);
      xhr.setRequestHeader('Content-Type', file.type || 'application/octet-stream');
      // Metadata that was bound to the presigned URL has to be honored by passing
      // in the meta data fields with x-amz-meta- prefixes
      xhr.setRequestHeader('x-amz-meta-name', file.name);
      xhr.send(file);
    }.bind(this));
  },

  clearAttachment: function(key) {
    var index = _.findIndex(this.attachmentViews, function(view) {
      return view.options.key === key;
    });
    this.attachmentViews[index].remove();
    this.attachmentViews.splice(index, 1);
  },

  save: function(e) {
    e.preventDefault();
    this.model.set({
      comment: this.editor.getContent('markdown'),
      commentHtml: this.editor.getContent('html'),
      files: _.map(this.attachmentViews, function(view) {
        return {
          key: view.options.key,
          name: view.options.name,
          size: view.options.size,
          previewUrl: view.options.previewUrl
        };
      })
    });
    comments.add(this.model);
    this.model.save();
    this.$status.hide().html('Your comment was saved.').fadeIn();
  }
});

module.exports = CommentView;
