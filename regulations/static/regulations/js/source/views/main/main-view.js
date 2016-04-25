'use strict';
var $ = require('jquery');
var _ = require('underscore');
var URI = require('urijs');
var DataTable = require('datatables.net')();
var Clipboard = require('clipboard');
var QueryCommand = require('query-command-supported');
var Backbone = require('backbone');
var SearchResultsView = require('./search-results-view');
var RegView = require('./reg-view');
var RegModel = require('../../models/reg-model');
var SearchModel = require('../../models/search-model');
var SubHeadView = require('../header/sub-head-view');
var SectionFooter = require('./section-footer-view');
var MainEvents = require('../../events/main-events');
var SidebarEvents = require('../../events/sidebar-events');
var DiffModel = require('../../models/diff-model');
var PreambleModel = require('../../models/preamble-model');
var DiffView = require('./diff-view');
var Router = require('../../router');
var HeaderEvents = require('../../events/header-events');
var DrawerEvents = require('../../events/drawer-events');
var Helpers = require('../../helpers');
var MainEvents = require('../../events/main-events');
var ChildView = require('./child-view');
var CommentReviewView = require('../comment/comment-review-view');
var CommentConfirmView = require('../comment/comment-confirm-view');
var PreambleView = require('./preamble-view');
var Resources = require('../../resources');
Backbone.$ = $;

var MainView = Backbone.View.extend({
    el: '#content-body',

    initialize: function() {
        this.dataTables = null;
        this.render = _.bind(this.render, this);

        if (Router.hasPushState) {
            this.listenTo(MainEvents, 'search-results:open', this.createView);
            this.listenTo(MainEvents, 'section:open', this.createView);
            this.listenTo(MainEvents, 'diff:open', this.createView);
            this.listenTo(MainEvents, 'breakaway:open', this.breakawayOpen);
            this.listenTo(MainEvents, 'section:error', this.displayError);
        }
        this.listenTo(MainEvents, 'section:resize', this.applyTablePlugin);
        this.listenTo(MainEvents, 'section:setHandlers', this.setHandlers);

        var childViewOptions = {},
            appendixOrSupplement;

        this.$topSection = this.$el.find('section[data-page-type]');

        // which page are we starting on?
        this.contentType = this.$topSection.data('page-type');
        // what version of the reg?
        this.regVersion = Helpers.findVersion(Resources.versionElements);
        // what section do we have open?
        this.sectionId = this.$topSection.attr('id');
        if (typeof this.sectionId === 'undefined') {
            //  Find the first child which *does* have a label
            this.sectionId = this.$topSection.find('section[id]').attr('id');
        }
        this.docId = $('#menu').data('doc-id');
        this.cfrTitle = $('#menu').data('cfr-title-number');

        // build options object to pass into child view constructor
        childViewOptions.id = this.sectionId;
        childViewOptions.regVersion = this.regVersion;
        childViewOptions.cfrTitle = this.cfrTitle;

        appendixOrSupplement = this.isAppendixOrSupplement();
        if (appendixOrSupplement) {
            // so that we will know what the doc title format should be
            childViewOptions.subContentType = appendixOrSupplement;
        }

        // find search query
        if (this.contentType === 'search-results') {
            childViewOptions.params = URI.parseQuery(window.location.search);
            childViewOptions.query = childViewOptions.params.q;
        }

        if (this.contentType === 'landing-page') {
            DrawerEvents.trigger('pane:change', 'table-of-contents');
        }

        // we don't want to ajax in data that the page loaded with
        childViewOptions.render = false;

        if (this.sectionId && this.modelmap[this.contentType]) {
            // store the contents of our $el in the model so that we
            // can re-render it later
            this.modelmap[this.contentType].set(this.sectionId, this.$el.html());
            childViewOptions.model = this.modelmap[this.contentType];
        }

        if (this.contentType && typeof this.viewmap[this.contentType] !== 'undefined') {
            // create new child view
            this.childView = new this.viewmap[this.contentType](childViewOptions);
        }

        this.sectionFooter = new SectionFooter({el: this.$el.find('.section-nav')});
    },

    modelmap: {
        'reg-section': RegModel,
        'landing-page': RegModel,
        'search-results': SearchModel,
        'diff': DiffModel,
        'appendix': RegModel,
        'interpretation': RegModel,
        'preamble-section': PreambleModel
    },

    viewmap: {
        'reg-section': RegView,
        'landing-page': RegView,
        'search-results': SearchResultsView,
        'diff': DiffView,
        'appendix': RegView,
        'interpretation': RegView,
        'comment-review': CommentReviewView,
        'comment-confirm': CommentConfirmView,
        'preamble-section': PreambleView
    },

    createView: function(id, options, type) {
        // close breakaway if open
        if (typeof this.breakawayCallback !== 'undefined') {
            this.breakawayCallback();
            delete(this.breakawayCallback);
        }

        this.contentType = type;

        // id is null on search results as there is no section id
        if (id !== null) {
            this.sectionId = id;
        }

        // this is a triage measure. I don't know how this could
        // ever be null, but apparently somewhere along the line it is
        if (this.regVersion === null) {
            this.regVersion = this.$el.find('section[data-page-type]').data('base-section');
        }

        if (typeof options.render === 'undefined') {
            // tell the child view it should render
            options.render = true;
        }

        options.id = id;
        options.type = this.contentType;
        options.regVersion = this.regVersion;
        options.docId = this.docId;
        options.model = this.modelmap[this.contentType];
        options.cb = this.render;
        options.cfrTitle = this.cfrTitle;

        // diffs need some more version context
        if (this.contentType === 'diff') {
            options.baseVersion = this.regVersion || Helpers.findVersion(Resources.versionElements);
            options.newerVersion = Helpers.findDiffVersion(Resources.versionElements);
            if (typeof options.fromVersion === 'undefined') {
                options.fromVersion = $('#table-of-contents').data('from-version');
            }
        }

        //search needs to know which version to search and switch to that version
        if (this.contentType === 'search-results' && typeof options.searchVersion !== 'undefined') {
            options.regVersion = options.searchVersion;
        }

        this.loading();
        SidebarEvents.trigger('section:loading');

        if (typeof this.childView !== 'undefined') {
            this.childView.remove();
            delete(this.childView);
        }

        this.childView = new this.viewmap[this.contentType](options);
    },

    isAppendixOrSupplement: function() {
        if (Helpers.isAppendix(this.sectionId)) {
            return 'appendix';
        }
        else if (Helpers.isSupplement(this.sectionId)) {
            return 'supplement';
        }
        return false;
    },

    breakawayOpen: function(cb) {
        this.breakawayCallback = cb;
        this.loading();
    },

    displayError: function() {
        // prevent error warning stacking
        $('.error-network').remove();

        // get ID of still rendered last section
        var oldId = this.$el.find('section[data-page-type]').attr('id'),
            $error = this.$el.prepend('<div class="error error-network"><span class="cf-icon cf-icon-error icon-warning"></span>Due to a network error, we were unable to retrieve the requested information.</div>').hide().fadeIn('slow');

        DrawerEvents.trigger('section:open', oldId);
        HeaderEvents.trigger('section:open', oldId);

        this.loaded();
        SidebarEvents.trigger('section:error');

        window.scrollTo($error.offset().top, 0);
    },

    render: function(html, options) {
        var offsetTop, $scrollToId;

        this.$el.html(html);

        // Destroy and recreate footer
        this.sectionFooter.remove();
        var $footer = this.$el.find('.section-nav');
        if ($footer) {
            this.sectionFooter = new SectionFooter({el: $footer});
        }

        MainEvents.trigger('section:rendered');

        SidebarEvents.trigger('update', {
            type: this.contentType,
            id: this.sectionId
        });

        if (options && typeof options.scrollToId !== 'undefined') {
            $scrollToId = $('#' + options.scrollToId);
            if ($scrollToId.length > 0) {
                offsetTop = $scrollToId.offset().top;
            }
        }

        window.scrollTo(0, offsetTop || 0);

        this.loaded();
    },

    loading: function() {
        // visually indicate that a new section is loading
        $('.main-content').addClass('loading');
    },

    loaded: function() {
        $('.main-content').removeClass('loading');

        // change focus to main content area when new sections are loaded
        $('.section-focus').focus();
        this.setHandlers();
    },

    setHandlers: function() {
        this.applyTablePlugin();
        this.applyClipboardPlugin();
    },

    applyClipboardPlugin: function() {
    // Create anchor tag for copy to clipboard
        if (document.queryCommandSupported('copy')) {
            this.$el.find('*[data-copyable="true"]').each(function(index, copyable) {
                var link = $('<a>', {
                    class: 'clipboard-link',
                    text: 'Copy this text to your clipboard',
                    title: 'Copy this text to your clipboard',
                    id: '#copyable-' + index,
                    href: '#copyable-' + index
                });
                var copylink = new Clipboard(link[0], {
                    target: function(trigger) {
                        return copyable;
                    }
                });
                $(copyable).before(link);
            });
        }
    },

    applyTablePlugin: function() {
        if (this.dataTables) {
            this.dataTables.destroy();
        }
        // Only apply the datatables plugin if there is a table header present
        if (this.$el.find('table').length) {
            this.dataTables = this.$el.find('table').has('thead *').DataTable({
                paging: false,
                searching: false,
                scrollY: 400,
                scrollCollapse: true,
                scrollX: true,
                info: false
            });
        }
    }

});
module.exports = MainView;
