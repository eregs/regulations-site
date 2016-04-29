'use strict';
var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
var Router = require('../../router');
var HeaderEvents = require('../../events/header-events');
var DrawerEvents = require('../../events/drawer-events');
var Helpers = require('../../helpers');
var Resources = require('../../resources');
var MainEvents = require('../../events/main-events');
var ChildView = require('./child-view');
Backbone.$ = $;

var DiffView = ChildView.extend({
    initialize: function(options) {
        this.options = options;
        this.id = this.options.id;
        this.baseVersion = this.options.baseVersion;
        this.newerVersion = this.options.newerVersion || Helpers.findDiffVersion(Resources.versionElements, this.baseVersion);
        this.fromVersion = this.options.fromVersion || this.newerVersion;
        // we preserve the section id as is in config obj because
        this.options.sectionId = this.id;

        this.url = 'diff/' + this.model.assembleDiffURL(this.options);
        ChildView.prototype.initialize.apply(this, arguments);

        if (typeof this.options.render === 'undefined') {
            DrawerEvents.trigger('pane:change', 'timeline');
        }
    },

    // "12 CFR Comparison of §1005.1 | eRegulations"
    assembleTitle: function() {
        var titleParts, newTitle;
        titleParts = _.compact(document.title.split(' '));
        newTitle = [titleParts[0], titleParts[1], Helpers.idToRef(this.id), '|', 'eRegulations'];
        return newTitle.join(' ');
    }
});

module.exports = DiffView;
