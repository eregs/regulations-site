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
    this.metadataUrl = this.$el.data('meta-url');

    this.listenTo(CommentEvents, 'read:proposal', this.handleRead);

    this.poll();
  },

  findElms: function() {
    this.$status = this.$el.find('.status');
  },

  handleRead: function() {
    var section = this.docId + '-preamble-' + this.docId + '-I';
    var options = {id: section, section: section, mode: 'read'};

    $('#content-body').removeClass('comment-review-wrapper');

    MainEvents.trigger('section:open', section, options, 'preamble-section');
  },

  poll: function() {
    this.interval = window.setInterval(
      function() {
        $.getJSON(this.metadataUrl).then(function(resp) {
          window.clearInterval(this.interval);
          this.setTrackingNumber(resp.trackingNumber);
        }.bind(this));
      }.bind(this),
      5000
    );
  },

  setTrackingNumber: function(number) {
    this.$status.html(
      '<div>Comment submitted</div>' +
      '<div>Tracking number: ' +
        '<a href="http://www.regulations.gov/#!searchResults;rpp=25;po=0;s=' + number + '">' + number + '</a>' +
      '</div>'
    );
  }
});

module.exports = CommentConfirmView;
