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

    this.findElms();

    this.docId = this.$el.data('doc-id');
    this.metadataUrl = this.$el.data('metadata-url');

    if (this.metadataUrl) {
      this.poll(this.metadataUrl);
      comments.filter(this.docId).forEach(function(comment) {
        comment.destroy();
      });
    }
  },

  findElms: function() {
    this.$pdf = this.$el.find('.pdf');
    this.$status = this.$el.find('.status');
  },

  poll: function(url) {
    this.interval = window.setInterval(
      function() {
        $.getJSON(url).then(function(resp) {
          this.setPdfUrl(resp.pdfUrl);
          if (resp.trackingNumber) {
            this.setTrackingNumber(resp.trackingNumber);
            window.clearInterval(this.interval);
          }
        }.bind(this));
      }.bind(this),
      5000
    );
  },

  setPdfUrl: function(url) {
    this.$pdf.html('<a href="' + url + '">Download PDF</a>');
  },

  setTrackingNumber: function(number) {
    this.$status.html('<div>Comment tracking number: ' + number + '</div>');
  }
});

module.exports = CommentConfirmView;
