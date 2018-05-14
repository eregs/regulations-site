

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');
const GAEvents = require('../events/ga-events');

Backbone.$ = $;

const AnalyticsHandler = Backbone.View.extend({
  initialize: function initialize() {
    GAEvents.on('section:open', this.sendEvent, 'open');
    GAEvents.on('definition:open', this.sendEvent, 'open');
    GAEvents.on('definition:close', this.sendEvent, 'close');
    GAEvents.on('interp:expand', this.sendEvent, 'expand');
    GAEvents.on('interp:collapse', this.sendEvent, 'collapse');
    GAEvents.on('interp:followCitation', this.sendEvent, 'click citation');
    GAEvents.on('definition:followCitation', this.sendEvent, 'click citation');
    GAEvents.on('sxs:open', this.sendEvent, 'open');
    GAEvents.on('drawer:open', this.sendEvent, 'open');
    GAEvents.on('drawer:close', this.sendEvent, 'close');
    GAEvents.on('drawer:switchTab', this.sendEvent, 'switch tab');

        // not sure if this works
    $('#timeline .stop-button').on('click', () => {
      this.sendEvent({ type: 'diff' }).bind('click stop comparing');
    });
  },

  sendEvent: function sendEvent(context) {
    const objectParts = [];
    let object = '';

    if (typeof window.ga === 'undefined') {
      return;
    }

    if (typeof context.type !== 'undefined') {
      objectParts.push(context.type);

      if (_.contains(['reg-section', 'definition', 'inline-interp', 'sxs', 'drawer'], context.type)) {
        if (typeof context.id !== 'undefined' && context.id !== null) {
          objectParts.push(context.id);
        }
      }
    }

    // diffs preserve ids in sectionId because
    // id has the url in order to keep a unique
    // instance cached in the model
    if (typeof context.sectionId !== 'undefined') {
      objectParts.push(context.sectionId);
    }

    if (typeof context.regVersion !== 'undefined') {
      objectParts.push(`version:${context.regVersion}`);
    }

    if (typeof context.baseVersion !== 'undefined' && typeof context.newerVersion !== 'undefined') {
      objectParts.push(`comparing:${context.baseVersion}`);
      objectParts.push(context.newerVersion);
    }

    if (typeof context.query !== 'undefined') {
      objectParts.push(`query:${context.query}`);
    }

    if (typeof context.page !== 'undefined') {
      objectParts.push(`results page:${context.page}`);
    }

    if (typeof context.from !== 'undefined') {
      objectParts.push(`from:${context.from}`);
    }

    if (typeof context.by !== 'undefined') {
      objectParts.push(`by:${context.by}`);
    }

    if (typeof context.to !== 'undefined') {
      objectParts.push(`to:${context.to}`);
    }

    if (typeof context.docNumber !== 'undefined') {
      objectParts.push(`doc:${context.docNumber}`);
    }

    object = objectParts.join(' ');

    window.ga('send', 'event', object, this);
  },
});

module.exports = AnalyticsHandler;
