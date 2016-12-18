

var $ = require('jquery');
var _ = require('underscore');
var Backbone = require('backbone');
var Helpers = require('../helpers');
var Resources = require('../resources');

Backbone.$ = $;

var MetaModel = Backbone.Model.extend({

  constructor: function constructor(properties) {
    var self = this;

    if (typeof properties !== 'undefined') {
      $.each(properties, function perProp(key, value) {
        self[key] = value;
      });
    }

    // in the case of reg-model
    // an index of all of the entities in the reg, whether or not they've been loaded
    this.content = this.content || {};

        // in the case of reg-model
        // content = markup to string representations of each reg paragraph/entity
        // loaded into the browser (rendered or not)
    this.structure = this.structure || [];

    Backbone.Model.apply(this, arguments);
  },

  set: function set(sectionId, sectionValue) {
    var cached = this.has(sectionId);
    var section;

    if (typeof sectionId !== 'undefined' && !(_.isEmpty(sectionId))) {
      if (!(cached)) {
        this.content[sectionId] = sectionValue;
        section = sectionValue;

        if (_.indexOf(this.structure, sectionId) === -1) {
          this.structure.push(sectionId);
        }
      } else {
        section = cached;
      }
    }
    return section;
  },

  has: function has(id) {
    return !!this.content[id];
  },

  get: function get(id, options) {
    return this.has(id) ?
        $.when(this.content[id]) :
        this.request(id, options);
  },

  request: function request(id, options) {
    return $.ajax({
      url: this.getAJAXUrl(id, options),
      success: function success(data) {
        this.set(id, data);
      }.bind(this),
    });
  },

  getAJAXUrl: function getAJAXUrl(id) {
    var url = window.APP_PREFIX + 'partial/';

    if (typeof this.supplementalPath !== 'undefined') {
      url += this.supplementalPath + '/';
    }

    url += id;

    if (id.indexOf('/') === -1) {
      url += '/' + Helpers.findVersion(Resources.versionElements);
    }

    return url;
  },
});

module.exports = MetaModel;
