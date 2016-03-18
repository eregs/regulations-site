'use strict';

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var CommentView = require('./comment-view');

var CommentReviewView = Backbone.View.extend({
  events: {
    'click #submit': 'submit'
  },

  initialize: function(options) {
    Backbone.View.prototype.setElement.call(this, '#' + options.id);
    this.template = $('#comment-template').html();
    this.$content = this.$el.find('#comment');
    this.docNumber = this.$el.data('doc-number');
    this.prefix = 'comment:' + this.docNumber;

    this.showComments();
  },

  render: function() {},

  showComments: function() {
    this.comments = _.chain(_.keys(window.localStorage))
      .filter(function(key) {
        return key.indexOf(this.prefix) === 0;
      }.bind(this))
      .map(function(key) {
        var payload = JSON.parse(window.localStorage.getItem(key));
        var section = key.replace('comment:', '');
        var $elm = $(_.template(this.template)({
          // TODO(jmcarp) Handle non-preamble sources
          url: ['', 'preamble'].concat(section.split('-')).join('/'),
          section: section,
          title: payload.title
        }));
        $elm.appendTo(this.$content);
        return new CommentView({el: $elm});
      }.bind(this))
      .value();
  },

  serialize: function() {
    return {
      docNumber: this.docNumber,
      sections: _.chain(_.keys(window.localStorage))
        .filter(function(key) {
          return key.indexOf(this.prefix) === 0;
        }.bind(this))
        .map(function(key) {
          return JSON.parse(window.localStorage.getItem(key));
        })
        .value()
    };
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
    // TODO(jmcarp) Figure out desired behavior
  },

  submitError: function() {
    // TODO(jmcarp) Figure out desired behavior
  }
});

module.exports = CommentReviewView;
