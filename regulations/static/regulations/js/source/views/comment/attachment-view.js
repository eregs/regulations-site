

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');

Backbone.$ = $;

const CommentEvents = require('../../events/comment-events');

const AttachmentView = Backbone.View.extend({
  events: {
    'click .attachment-remove': 'handleRemove',
  },

  initialize: function initialize(options) {
    this.template = _.template(document.querySelector('#comment-attachment-template').innerHTML);
    this.options = options;

    if (this.options.xhr) {
      this.options.xhr.upload.addEventListener('progress', this.handleProgress.bind(this));
      this.options.xhr.upload.addEventListener('load', this.handleLoad.bind(this));
    }

    this.render();
    this.$progress = this.$el.find('.attachment-progress');
  },

  render: function render() {
    const $el = $(this.template(this.options));
    this.options.$parent.append($el);
    this.setElement($el);
  },

  handleProgress: function handleProgress(e) {
    const percent = e.loaded / e.total;
    this.$progress.text(Math.round(percent * 1000) / 10);
  },

  handleLoad: function handleLoad() {
    this.$progress.empty();
  },

  handleRemove: function handleRemove() {
    CommentEvents.trigger('attachment:remove', this.options.key);
    if (this.options.xhr) {
      this.options.xhr.abort();
    }
  },
});

module.exports = AttachmentView;
