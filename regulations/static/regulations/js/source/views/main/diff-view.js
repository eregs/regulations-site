import storage from '../../redux/storage';
import { paneActiveEvt } from '../../redux/paneReduce';

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');
const Helpers = require('../../helpers');
const Resources = require('../../resources');
const ChildView = require('./child-view');

Backbone.$ = $;

const DiffView = ChildView.extend({
  initialize: function initialize(options, ...args) {
    this.options = options;
    this.id = this.options.id;
    this.baseVersion = this.options.baseVersion;
    this.newerVersion = this.options.newerVersion || Helpers.findDiffVersion(
      Resources.versionElements, this.baseVersion);
    this.fromVersion = this.options.fromVersion || this.newerVersion;
        // we preserve the section id as is in config obj because
    this.options.sectionId = this.id;

    this.url = `diff/${this.model.assembleDiffURL(this.options)}`;
    ChildView.prototype.initialize.apply(this, [options].concat(args));

    if (typeof this.options.render === 'undefined') {
      storage().dispatch(paneActiveEvt('timeline'));
    }
  },

  // "12 CFR Comparison of §1005.1 | eRegulations"
  assembleTitle: function assembleTitle() {
    const titleParts = _.compact(document.title.split(' '));
    const newTitle = [titleParts[0], titleParts[1], this.sectionLabel, '|', 'eRegulations'];
    return newTitle.join(' ');
  },
});

module.exports = DiffView;
