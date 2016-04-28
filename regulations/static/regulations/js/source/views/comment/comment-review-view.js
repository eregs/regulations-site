'use strict';

var $ = require('jquery');
var URI = require('urijs');
var _ = require('underscore');
var Backbone = require('backbone');
Backbone.$ = $;

var MainEvents = require('../../events/main-events');
var CommentEvents = require('../../events/comment-events');
var comments = require('../../collections/comment-collection');

var CommentReviewView = Backbone.View.extend({
  events: {
    'click .edit-comment': 'editComment',
    'click .preview-button': 'preview',
    'change .agree': 'toggleSubmit'
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
    this.$form = this.$el.find('form');
  },

  editComment: function(e) {
    var section = $(e.target).closest('li').data('section');
    var options = {id: section, section: section, mode: 'write'};

    $('#content-body').removeClass('comment-review-wrapper');

    MainEvents.trigger('section:open', section, options, 'preamble-section');
    CommentEvents.trigger('comment:writeTabOpen');
  },

  render: function() {
    var commentData = comments.toJSON({docId: this.docId});
    var html = this.template({
      comments: commentData,
      previewLoading: this.previewLoading
    });

    this.$content.html(html);
    this.findElms();

    this.initTabs();
    this.initDependencies();

    this.$form.find('[name="comments"]').val(JSON.stringify(commentData));

    CommentEvents.trigger('comment:writeTabOpen');
  },

  initTabs: function() {
    function updateTabs(tab, tabSet) {
      var tabSelector = '[data-tab="' + tab + '"]';
      var setSelector = '[data-tab-set="' + tabSet + '"]';
      $(setSelector).removeClass('current');
      $(setSelector + tabSelector).addClass('current');
      $(setSelector + '[data-tabs]').each(function(idx, elm) {
        var $elm = $(elm);
        var tabs = $elm.data('tabs');
        if (tabs.indexOf(tab) !== -1) {
          $elm.show();
        } else {
          $elm.hide();
        }
      });
    }
    var $tabs = $('[data-tab]');
    updateTabs($tabs.data('tab'), $tabs.data('tab-set'));
    $tabs.on('click', function() {
      var $tab = $(this);
      updateTabs($tab.data('tab'), $tab.data('tab-set'));
    });
  },

  initDependencies: function() {
    $('select[data-depends-on]').each(function(idx, elm) {
      var $elm = $(elm);
      var $dependsOn = $('[name="' + $elm.data('depends-on') + '"]');
      var $options = $elm.find('option[value]').detach().clone();
      function updateOptions(value) {
        $elm.find('option[value]').remove();
        $options.filter(function(idx, elm) {
          return $(elm).data('dependency') === value;
        }).appendTo($elm);
        $elm.val(null);
      }
      updateOptions.apply($dependsOn);
      $dependsOn.on('change', function() {
        updateOptions($(this).val());
      });
    });
  },

  preview: function() {
    var $xhr = $.ajax({
      type: 'POST',
      url: window.APP_PREFIX + 'comments/preview',
      data: JSON.stringify({
        assembled_comment: comments.toJSON({docId: this.docId})
      }),
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

  toggleSubmit: function() {
    $('.submit-button').prop('disabled', function(i, v) { return !v; });
  }
});

module.exports = CommentReviewView;
