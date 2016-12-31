

const $ = require('jquery');
const Backbone = require('backbone');
const HeaderEvents = require('../../events/header-events');

Backbone.$ = $;

const SubHeadView = Backbone.View.extend({
  el: '#content-header',

  initialize: function initialize() {
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
  changeTitle: function changeTitle(label) {
    this.$activeTitle.html(label);
  },

  displayCount: function displayCount(resultCount) {
    this.$activeTitle.html(`<span class="subpart">Search results</span> ${resultCount}`);
  },

  changeDate: function changeDate() {
    this.version = $('section[data-base-version]').data('base-version');
    if (this.version) {
      this.displayDate = $(`select[name="version"] option[value="${this.version}"]`).text();
      $('.effective-date').html(`<strong>Effective date:</strong> ${this.displayDate}`);
    } else {
      $('.effective-date').html('');
    }
  },

  renderSubpart: function renderSubpart(label) {
    this.$subpartLabel.text(label).show();
    this.$activeTitle.addClass('with-subpart');
  },

  removeSubpart: function removeSubpart() {
    this.$subpartLabel.text('').hide();
    this.$activeTitle.removeClass('with-subpart');
  },

  reset: function reset() {
    this.$activeTitle.html('');
  },
});

module.exports = SubHeadView;
