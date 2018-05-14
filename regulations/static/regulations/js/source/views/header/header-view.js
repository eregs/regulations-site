

const $ = require('jquery');
const Backbone = require('backbone');
const SubHead = require('./sub-head-view');

Backbone.$ = $;

const HeaderView = Backbone.View.extend({
  el: '.reg-header',

  initialize: function initialize() {
    this.subHeadView = new SubHead();
  },

  events: {
    'click .mobile-nav-trigger': 'toggleNav',
  },

  toggleNav: function toggleNav(e) {
    e.preventDefault();
    $('.app-nav-list, .mobile-nav-trigger').toggleClass('open');
  },

  contextMap: {
    changeSubHeadText: '_updateSubHead',
  },

  ask: function ask(message, context) {
    if (typeof this.contextMap[message] !== 'undefined') {
      this.contextMap[message].apply(context);
    }
  },

    // type = wayfinding or search
    // content = new content
  _updateSubHead: function _updateSubHead(context) {
    this.subHeadView.change(
            context.type,
            context.content,
        );
  },
});

module.exports = HeaderView;
