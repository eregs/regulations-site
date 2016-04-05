'use strict';

var $ = require('jquery');
var URI = require('urijs');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var comments = require('../../collections/comment-collection');

var CommentReviewView = Backbone.View.extend({
  events: {
    'click .preview-button': 'preview',
    'click .submit-button': 'submit'
  },

  initialize: function(options) {
    Backbone.View.prototype.setElement.call(this, '#' + options.id);

    this.$content = this.$el.find('.comment-review-items');

    this.docId = this.$el.data('doc-id');
    this.template = _.template($('#comment-template').html());

    this.previewLoading = false;
    this.render();
  },

  findElms: function() {
    this.$status = this.$el.find('.status');
  },

  render: function() {
    var commentData = comments.toJSON({docId: this.docId});
    var html = this.template({
      comments: commentData,
      previewLoading: this.previewLoading
    });
    this.$content.html(html);
    this.findElms();
  },

  serialize: function() {
    return {
      sections: comments.toJSON({docId: this.docId})
    };
  },

  preview: function() {
    var $xhr = $.ajax({
      type: 'POST',
      url: window.APP_PREFIX + 'comments/preview',
      data: JSON.stringify(this.serialize()),
      contentType: 'application/json',
      dataType: 'json'
    });
    $xhr.then(this.previewSuccess.bind(this));
    this.previewLoading = true;
    this.render();
  },

  previewSuccess: function(resp) {
    window.location = resp.url;
    this.previewLoading = false;
    this.render();
  },

  submit: function() {
    var prefix = window.APP_PREFIX || '/';
    var $xhr = $.ajax({
      type: 'POST',
      url: prefix + 'comments/comment',
      data: JSON.stringify(this.serialize()),
      contentType: 'application/json',
      dataType: 'json'
    });
    $xhr.done(this.submitSuccess.bind(this));
    $xhr.fail(this.submitError.bind(this));
  },

  submitSuccess: function(resp) {
    this.$status.text('Comment processing').fadeIn();
    this.poll(resp.metadata_url);
  },

  submitError: function() {
    // TODO(jmcarp) Figure out desired behavior
  },

  poll: function(url) {
    this.interval = window.setInterval(
      function() {
        $.getJSON(url).then(function(resp) {
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

module.exports = CommentReviewView;
