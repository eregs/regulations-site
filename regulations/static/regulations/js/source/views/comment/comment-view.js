import storage from '../../redux/storage';
import { locationActiveEvt } from '../../redux/locationReduce';
import { paneActiveEvt } from '../../redux/paneReduce';

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');
const filesize = require('filesize');

Backbone.$ = $;

const edit = require('prosemirror/dist/edit');
const menu = require('prosemirror/dist/menu/menu');
require('prosemirror/dist/menu/menubar');
require('prosemirror/dist/markdown');

const MainEvents = require('../../events/main-events');
const CommentModel = require('../../models/comment-model').CommentModel;
const CommentEvents = require('../../events/comment-events');
const AttachmentView = require('../../views/comment/attachment-view');
const comments = require('../../collections/comment-collection');
const helpers = require('../../helpers');

const MAX_ATTACHMENTS = 9;

/**
 * Get a presigned upload URL.
 * The file extension (from the name) and size are validated
 * and the uploadURL is constrained by the file name and size.
 *
 * @param file {File} File to upload
 */
function getUploadUrl(file) {
  return $.getJSON(
    `${window.APP_PREFIX}comments/attachment`,
    { size: file.size, name: file.name, type: file.type || 'application/octet-stream' },
  ).then(resp => resp);
}

const CommentView = Backbone.View.extend({
  events: {
    'change input[type="file"]': 'addAttachments',
    'dragenter input[type="file"]': 'highlightDropzone',
    'dragleave input[type="file"]': 'unhighlightDropzone',
    'click .comment-header': 'openComment',
    'click .comment-context-toggle': 'toggleCommentExcerpt',
    'click .comment-delete-response': 'deleteComment',
    'submit form': 'save',
  },

  initialize: function initialize(options) {
    this.options = options;

    this.$context = this.$el.find('.comment-context');
    this.$contextSectionLabel = this.$el.find('.comment-context-section');
    this.$header = this.$el.find('.comment-header');
    this.$headerLink = this.$el.find('.comment-header-link');
    this.$deleteResponseDiv = this.$el.find('.comment-delete-response');
    this.$container = this.$el.find('.editor-container');
    this.$input = this.$el.find('input[type="file"]');
    this.$attachmentCount = this.$el.find('.comment-attachment-count');
    this.$attachmentLimit = this.$el.find('.comment-attachment-limit');
    this.$attachments = this.$el.find('.comment-attachments');
    this.$status = this.$el.find('.status');

    const hrGroup = new menu.MenuCommandGroup('insert');
    const headingMenu = new menu.Dropdown({
      label: 'Heading', displayActive: true,
    }, [new menu.MenuCommandGroup('textblock'), new menu.MenuCommandGroup('textblockHeading')]);
    this.editor = new edit.ProseMirror({
      menuBar: { content: [menu.inlineGroup, headingMenu, menu.blockGroup, hrGroup] },
      commands: edit.CommandSet.default.update({
        'code:toggle': { menu: null },
        'code_block:make': { menu: null },
        'image:insert': { menu: null },
        selectParentNode: { menu: null },
      }),
      place: this.$container.get(0),
      docFormat: 'markdown',
      doc: '',
    });

    this.attachmentViews = [];

    this.listenTo(CommentEvents, 'comment:target', this.target);
    this.listenTo(CommentEvents, 'attachment:remove', this.clearAttachment);

    this.setSection(options.section, options.tocId, options.indexes, options.label);
  },

  setSection: function setSection(section, tocId, indexes, label, blank) {
    if (this.model) {
      this.stopListening(this.model);
    }
    const options = {
      id: section,
      tocId,
      indexes,
      label,
      docId: this.options.docId,
    };
    this.model = blank ?
      new CommentModel(options) :
      comments.get(section) || new CommentModel(options);
    this.listenTo(this.model, 'destroy', this.setSection.bind(this, section, tocId, indexes, label, true));

    this.render();
  },

  target: function target(options) {
    this.setSection(options.section, options.tocId, options.indexes, options.label);
    this.$context.empty();
    if (options.$parent) {
      let label = options.label;
      const parsed = helpers.parsePreambleId(options.section);
      const href = `${window.APP_PREFIX + parsed.path.join('/')}#${parsed.hash}`;
      // Splice section label and context title, if present
      // TODO: Build this upstream
      const $sectionHeader = options.$parent.find('.node:first :header');
      if ($sectionHeader.length) {
        label = [label, $sectionHeader.text().split('. ').slice(1)].join('. ');
        $sectionHeader.remove();
      }
      this.$headerLink.html(`<a href="${href}">${label}</a>`);

      this.$contextSectionLabel.html(options.label);

      this.$deleteResponseDiv.attr('data-section', options.section);

      this.$context.append(options.$parent);
    }
  },

  openComment: function openComment(e) {
    e.preventDefault();
    const options = {
      section: this.model.get('id'),
      tocId: this.model.get('tocId'),
      label: this.model.get('label'),
    };
    // TODO: Push this logic into `PreambleView`
    const type = options.section.split('-')[1];
    storage().dispatch(locationActiveEvt(options.tocId));
    storage().dispatch(paneActiveEvt(type === 'preamble' ? 'table-of-contents' : 'table-of-contents-secondary'));
    MainEvents.trigger('section:open', options.section, options, 'preamble-section');
  },

  toggleCommentExcerpt: function toggleCommentExcerpt() {
    $('.comment-context-text-show').toggle();
    $('.comment-context-text-hide').toggle();
    $('.fa-plus-circle').toggle();
    $('.fa-minus-circle').toggle();
    $('.comment-context').toggle();
  },

  render: function render() {
    this.editor.setContent(this.model.get('comment'), 'markdown');
    this.$attachments.empty();
    this.attachmentViews = this.model.get('files').map(file => new AttachmentView(_.extend({ $parent: this.$attachments }, file)));
    this.setAttachmentCount();
    this.$attachmentLimit.html(`<strong>Limit</strong>: ${MAX_ATTACHMENTS} total attachments.`);
  },

  highlightDropzone: function highlightDropzone() {
    this.$input.addClass('highlight');
  },

  unhighlightDropzone: function unhighlightDropzone() {
    this.$input.removeClass('highlight');
  },

  addAttachments: function addAttachments(e) {
    if (this.attachmentCount + e.target.files.length > MAX_ATTACHMENTS) {
      this.$status.text('Too many attachments');
      return;
    }
    _.each(e.target.files, (file) => {
      this.addAttachment(file);
    });
    this.$input.val(null);
    this.unhighlightDropzone();
  },

  /**
   * Upload an attachment. Request a signed upload URL, PUT the file via
   * XMLHttpRequest, and pass the XHR to AttachmentView for rendering.
   *
   * @param {File} file File to upload
   */
  addAttachment: function addAttachment(file) {
    getUploadUrl(file).then((resp) => {
      const xhr = new XMLHttpRequest();
      this.attachmentViews.push(
        new AttachmentView({
          $parent: this.$attachments,
          previewUrl: resp.urls.get,
          name: file.name,
          size: filesize(file.size),
          key: resp.key,
          xhr,
        }),
      );
      this.setAttachmentCount();
      xhr.open('PUT', resp.urls.put);
      xhr.setRequestHeader('Content-Type', file.type || 'application/octet-stream');
      // Metadata that was bound to the presigned URL has to be honored by passing
      // in the meta data fields with x-amz-meta- prefixes
      xhr.setRequestHeader('x-amz-meta-name', file.name);
      xhr.send(file);
    });
  },

  clearAttachment: function clearAttachment(key) {
    const index = _.findIndex(this.attachmentViews, view => view.options.key === key);
    this.attachmentViews[index].remove();
    this.attachmentViews.splice(index, 1);
    this.setAttachmentCount();
  },

  setAttachmentCount: function setAttachmentCount() {
    // Count saved attachments on other comments and pending attachments on the
    // current comment
    let count = comments.filter(this.options.docId).reduce((total, comment) => {
      const incr = comment.id !== this.model.id ?
        comment.get('files').length :
        0;
      return total + incr;
    }, 0);
    count += this.attachmentViews.length;
    this.attachmentCount = count;
    const plural = this.attachmentCount !== 1 ? 's' : '';
    this.$attachmentCount.text(`You've uploaded ${this.attachmentCount} total attachment${plural}.`);
    this.$input.prop('disabled', this.attachmentCount >= MAX_ATTACHMENTS);
  },

  deleteComment: function deleteComment(e) {
    e.preventDefault();

    const comment = comments.get($(e.target).data('section'));
    if (comment) {
      comment.destroy();

      this.editor.setContent('', 'html');
      this.$status.hide().html('Your comment was deleted.').fadeIn();
    }
  },

  save: function save(e) {
    e.preventDefault();

    this.model.set({
      comment: this.editor.getContent('markdown'),
      commentHtml: this.editor.getContent('html'),
      files: _.map(this.attachmentViews, view => ({
        key: view.options.key,
        name: view.options.name,
        size: view.options.size,
        previewUrl: view.options.previewUrl,
      })),
    });

    comments.add(this.model);
    this.model.save();
    this.$status.hide().html('Your comment was saved.').fadeIn();
  },
});

module.exports = CommentView;
