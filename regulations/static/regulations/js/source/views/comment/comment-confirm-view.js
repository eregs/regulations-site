'use strict';

var $ = require('jquery');
var URI = require('urijs');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var MainEvents = require('../../events/main-events');
var PreambleHeadView = require('../header/preamble-head-view');
var CommentEvents = require('../../events/comment-events');
var comments = require('../../collections/comment-collection');

var CommentConfirmView = Backbone.View.extend({
  initialize: function(options) {
    Backbone.View.prototype.setElement.call(this, '#' + options.id);

    this.findElms();

    this.docId = this.$el.data('doc-id');
    this.metaUrl = this.$el.data('meta-url');

    this.listenTo(CommentEvents, 'read:proposal', this.handleRead);

    if (this.metaUrl) {
      this.poll(this.metaUrl);
      comments.filter(this.docId).forEach(function(comment) {
        comment.destroy();
      });
    }
  },

  findElms: function() {
    this.$pdf = this.$el.find('.pdf');
    this.$status = this.$el.find('.status');
  },

  handleRead: function() {
    var section = this.docId + '-preamble-' + this.docId + '-I';
    var options = {id: section, section: section, mode: 'read'};

    $('#content-body').removeClass('comment-review-wrapper');

    MainEvents.trigger('section:open', section, options, 'preamble-section');
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
