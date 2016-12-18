'use strict';

var $ = require('jquery');
var URI = require('urijs');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var MainEvents = require('../../events/main-events');
var CommentEvents = require('../../events/comment-events');
var comments = require('../../collections/comment-collection');

var CommentConfirmView = Backbone.View.extend({
  initialize: function(options) {
    Backbone.View.prototype.setElement.call(this, '#' + options.id);

    this.docId = this.$el.data('doc-id');
    this.metadataUrl = this.$el.data('metadata-url');

    if (this.metadataUrl) {
      this.poll(this.metadataUrl);
      comments.filter(this.docId).forEach(function(comment) {
        comment.destroy();
      });
    }
  },

  poll: function(url) {
    this.interval = window.setInterval(
      function() {
        $.getJSON(url).then(function(resp) {
          if (resp.error) {
            this.setRegsGovError();
          } else {
            this.setPdfUrl(resp.pdfUrl);
            this.setTrackingNumber(resp.trackingNumber);
          }
          window.clearInterval(this.interval);
        }.bind(this));
      }.bind(this),
      5000,
    );
  },

  /**
   * Fill in an element's (indicated by the selector) template with the ctx
   * provided
   **/
  replaceTemplate: function(selector, ctx, tplSelector) {
    if (!tplSelector) {
      tplSelector = '.js-template';
    }
    this.$el.find(selector).each(function(idx, elt) {
      var $elt = $(elt);
      var $tplElt = $elt.find(tplSelector);
      var result = _.template($tplElt.prop('innerHTML'))(ctx);
      $elt.empty();
      $elt.append($tplElt);
      $elt.append(result);
    });
  },

  setPdfUrl: function(url) {
    this.replaceTemplate('.save-pdf', {url: url});
  },

  // Changes text and color of background when tracking number is received, hides wait message
  setTrackingNumber: function(number) {
    this.replaceTemplate('.tracking-number .status', {number: number});
    this.$el.find('.status').addClass('tracking-number-retrieved');
    this.$el.find('.status-waiting').hide();
  },

  setRegsGovError: function() {
    this.replaceTemplate('.status-container', {}, '.js-regsgov-error');
  },
});

module.exports = CommentConfirmView;
