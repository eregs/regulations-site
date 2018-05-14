

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');
const Helpers = require('../helpers');
const Resources = require('../resources');

Backbone.$ = $;

const MetaModel = Backbone.Model.extend({

  constructor: function constructor(properties, ...args) {
    const self = this;

    if (typeof properties !== 'undefined') {
      $.each(properties, (key, value) => {
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

    Backbone.Model.apply(this, [properties].concat(args));
  },

  set: function set(sectionId, sectionValue) {
    const cached = this.has(sectionId);
    let section;

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
    let url = `${window.APP_PREFIX}partial/`;

    if (typeof this.supplementalPath !== 'undefined') {
      url += `${this.supplementalPath}/`;
    }

    url += id;

    if (id.indexOf('/') === -1) {
      url += `/${Helpers.findVersion(Resources.versionElements)}`;
    }

    return url;
  },
});

module.exports = MetaModel;
