

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');

Backbone.$ = $;

const comments = require('../../collections/comment-collection');

const CommentConfirmView = Backbone.View.extend({
  initialize: function initialize(options) {
    Backbone.View.prototype.setElement.call(this, `#${options.id}`);

    this.docId = this.$el.data('doc-id');
    this.metadataUrl = this.$el.data('metadata-url');

    if (this.metadataUrl) {
      this.poll(this.metadataUrl);
      comments.filter(this.docId).forEach((comment) => {
        comment.destroy();
      });
    }
  },

  poll: function poll(url) {
    this.interval = window.setInterval(
      () => {
        $.getJSON(url).then((resp) => {
          if (resp.error) {
            this.setRegsGovError();
          } else {
            this.setPdfUrl(resp.pdfUrl);
            this.setTrackingNumber(resp.trackingNumber);
          }
          window.clearInterval(this.interval);
        });
      },
      5000,
    );
  },

  /**
   * Fill in an element's (indicated by the selector) template with the ctx
   * provided
   **/
  replaceTemplate: function replaceTemplate(selector, ctx, tplSelector = '.js-template') {
    this.$el.find(selector).each((idx, elt) => {
      const $elt = $(elt);
      const $tplElt = $elt.find(tplSelector);
      const result = _.template($tplElt.prop('innerHTML'))(ctx);
      $elt.empty();
      $elt.append($tplElt);
      $elt.append(result);
    });
  },

  setPdfUrl: function setPdfUrl(url) {
    this.replaceTemplate('.save-pdf', { url });
  },

  // Changes text and color of background when tracking number is received, hides wait message
  setTrackingNumber: function setTrackingNumber(number) {
    this.replaceTemplate('.tracking-number .status', { number });
    this.$el.find('.status').addClass('tracking-number-retrieved');
    this.$el.find('.status-waiting').hide();
  },

  setRegsGovError: function setRegsGovError() {
    this.replaceTemplate('.status-container', {}, '.js-regsgov-error');
  },
});

module.exports = CommentConfirmView;
