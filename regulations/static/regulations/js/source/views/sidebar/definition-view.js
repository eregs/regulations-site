import React from 'react';
import ReactDOM from 'react-dom';
import Definitions from './definitions';

const $ = require('jquery');
const Backbone = require('backbone');
const Helpers = require('../../helpers');
const Router = require('../../router');
const MainEvents = require('../../events/main-events');
const SidebarEvents = require('../../events/sidebar-events');
const GAEvents = require('../../events/ga-events');

Backbone.$ = $;

// **Constructor**
// this.options:
//
// * **id** string, dash-delimited id of definition paragraph
// * **$anchor** jQobj, the reg-view link that opened the def
//
// this.options turns into this.model
const DefinitionView = Backbone.View.extend({
  el: '#definition',

  events: {
    'click .close-button': 'close',
    'click .update-definition': 'updateDefinition',
  },

  initialize: function initialize(options) {
    this.options = options;
    this.listenTo(SidebarEvents, 'definition:outOfScope', this.displayScopeMsg);
    this.listenTo(SidebarEvents, 'definition:inScope', this.removeScopeMsg);
    this.listenTo(SidebarEvents, 'definition:activate', this.unGrayDefinition);
    this.listenTo(SidebarEvents, 'definition:deactivate', this.grayOutDefinition);

    if (typeof this.options.id !== 'undefined') {
      this.id = this.options.id;
    }

    if (typeof this.options.term !== 'undefined') {
      this.term = this.options.term;
      this.$el.data('defined-term', this.term);
    }

    // insert the spinner header to be replaced
    // by the full def once it loads
    ReactDOM.render(React.createElement(Definitions, { loading: true }),
                    this.$el[0]);

    // if pushState is supported, attach the
    // appropriate event handlers
    if (Router.hasPushState) {
      this.events['click .continue-link.interp'] = 'openInterpretation';
      this.events['click .continue-link.full-def'] = 'openFullDefinition';
      this.events['click .definition'] = 'openFullDefinition';
      this.delegateEvents(this.events);
    }
  },

  render: function render(html) {
    this.$el.html(html);
  },

  renderError: function renderError() {
    ReactDOM.render(
      React.createElement(Definitions, { errorId: this.id }),
      this.$el[0],
    );
  },

  close: function close(e) {
    e.preventDefault();
        // return focus to the definition link once the definition is removed
    $('.definition.active').focus();

    MainEvents.trigger('definition:close');
    GAEvents.trigger('definition:close', {
      type: 'definition',
      by: 'header close button',
    });
    this.remove();
  },

  updateDefinition: function updateDefinition(e) {
    e.preventDefault(e);

    SidebarEvents.trigger('definition:open', {
      id: $(e.target).data('definition'),
      term: this.term,
      cb: function cb() {
                // update list of out of scope paragraphs for new definition
        MainEvents.trigger('definition:carriedOver');
      },
    });
  },

  // displayed when an open definition doesn't apply to the
  // whole open section
  displayScopeMsg: function displayScopeMsg(id) {
    let msg = '<p>This term has a different definition for some portions of ';
    msg += id ? `${$(`#${id}`).data('label')}.` : 'this section.';
    msg += '</p>';

    this.$warningContainer = this.$warningContainer || this.$el.find('.definition-warning');

    this.$warningContainer.removeClass('hidden')
                              .find('.msg').html(msg);
  },

    // when a definition is fully applicable to the section
  removeScopeMsg: function removeScopeMsg() {
    if (typeof this.$warningContainer !== 'undefined' && this.$warningContainer.length > 0) {
      this.$warningContainer.addClass('hidden').find('.msg').html('');
    }

    this.unGrayDefinition();
  },

  // for when the definition does not apply to the active section
  grayOutDefinition: function grayOutDefinition(defId, href, activeSectionId) {
    const $text = this.$el.find('.definition-text');
    let linkText = 'Load the correct definition for ';
    const $msg = this.$warningContainer.find('.msg');
    let link;

    if (typeof this.$warningContainer === 'undefined') {
      this.displayScopeMsg(Helpers.findBaseSection(activeSectionId));
    }

    linkText += (defId) ? $(`#${activeSectionId}`).data('label') : 'this section';
    link = `<a href="${href}" class="update-definition inactive internal" data-definition="${defId}">`;
    link += `${linkText}</a>`;

        // remove duplicates
    $msg.find('a').remove();

        // insert link to load applicable definition
    $msg.append(link);

        // gray out definition text
    $text.addClass('inactive');
  },

    // for when a definition is not in conflict for the active section,
    // but doesn't apply to the entire section, either
  unGrayDefinition: function unGrayDefinition() {
    const $text = this.$el.find('.definition-text');
    $text.removeClass('inactive');

    this.$el.find('.definition-warning a').remove();
  },

  openFullDefinition: function openFullDefinition(e) {
    e.preventDefault();
    const id = $(e.target).data('linked-section') || $(e.target).data('definition');
    const parentId = Helpers.findBaseSection(id);

    MainEvents.trigger('section:open', parentId, {
      scrollToId: id,
    }, 'reg-section');

    GAEvents.trigger('definition:followCitation', {
      id,
      type: 'definition',
    });
  },

  openInterpretation: function openInterpretation(e) {
    e.preventDefault();
    const $e = $(e.target);
    const id = $e.data('linked-section');
    const pid = $e.data('linked-subsection');

    MainEvents.trigger('section:open', id, {
      scrollToId: pid,
    }, 'interpretation');

    GAEvents.trigger('definition:followCitation', {
      id,
      type: 'definition',
    });
  },

  remove: function remove() {
    this.stopListening();
    this.off();
    this.$el.html('');

    return this;
  },
});

module.exports = DefinitionView;
