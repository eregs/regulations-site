'use strict';
var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
var RegsHelpers = require('../../helpers');
var HeaderEvents = require('../../events/header-events');
Backbone.$ = $;

var SubHeadView = Backbone.View.extend({
    el: '#content-header',

    initialize: function() {
        this.listenTo(HeaderEvents, 'section:open', this.changeTitle);
        this.listenTo(HeaderEvents, 'search-results:open', this.displayCount);
        this.listenTo(HeaderEvents, 'search-results:open', this.changeDate);
        this.listenTo(HeaderEvents, 'search-results:open', this.removeSubpart);
        this.listenTo(HeaderEvents, 'clear', this.reset);
        this.listenTo(HeaderEvents, 'subpart:present', this.renderSubpart);
        this.listenTo(HeaderEvents, 'subpart:absent', this.removeSubpart);

        // cache inner title DOM node for frequent reference
        this.$activeTitle = this.$el.find('.header-label');

        // same for subpart label
        this.$subpartLabel = this.$el.find('.subpart');
    },

    // populates subhead (.header-label) with new title depending on viewport location
    // ex: §478.1(a) to §478.1(b)
    changeTitle: function(id) {
        this.$activeTitle.html(RegsHelpers.idToRef(id));
    },

    displayCount: function(resultCount) {
        this.$activeTitle.html('<span class="subpart">Search results</span> ' + resultCount);
    },

    changeDate: function() {
        this.version = $('section[data-base-version]').data('base-version');
        if (this.version) {
          this.displayDate = $('select[name="version"] option[value="' + this.version + '"]').text();
          $('.effective-date').html('<strong>Effective date:</strong> ' + this.displayDate);
        } else {
          $('.effective-date').html('');
        }
    },

    renderSubpart: function(label) {
        this.$subpartLabel.text(label).show();
        this.$activeTitle.addClass('with-subpart');
    },

    removeSubpart: function() {
        this.$subpartLabel.text('').hide();
        this.$activeTitle.removeClass('with-subpart');
    },

    reset: function() {
        this.$activeTitle.html('');
    }
});

module.exports = SubHeadView;
