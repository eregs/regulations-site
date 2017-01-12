

const $ = require('jquery');
const Backbone = require('backbone');
const SxSList = require('./sxs-list-view');
const SidebarModel = require('../../models/sidebar-model');
const DefinitionModel = require('../../models/definition-model');
const SidebarEvents = require('../../events/sidebar-events');
const Definition = require('./definition-view');
const MainEvents = require('../../events/main-events');
const Helpers = require('../../helpers.js');

Backbone.$ = $;

const SidebarView = Backbone.View.extend({
  el: '#sidebar-content',

  events: {
    'click .expandable': 'toggleExpandable',
  },

  initialize: function initialize() {
    this.listenTo(SidebarEvents, 'update', this.updateChildViews);
    this.listenTo(SidebarEvents, 'definition:open', this.openDefinition);
    this.listenTo(SidebarEvents, 'definition:close', this.closeDefinition);
    this.listenTo(SidebarEvents, 'section:loading', this.loading);
    this.listenTo(SidebarEvents, 'section:error', this.loaded);
    this.listenTo(SidebarEvents, 'breakaway:open', this.hideChildren);

    this.childViews = { sxs: new SxSList() };
    this.definitionModel = DefinitionModel;
    this.model = SidebarModel;
        /* Cache the initial sidebar */
    this.$el.find('[data-cache-key=sidebar]').each((idx, el) => {
      const $el = $(el);
      SidebarModel.set($el.data('cache-value'), $el.html());
    });
  },

  openDefinition: function openDefinition(config) {
    this.childViews.definition = new Definition({
      id: config.id,
      term: config.term,
    });

    this.definitionModel.get(config.id, {}).then((resp) => {
      this.childViews.definition.render(resp);
    }).fail(this.childViews.definition.renderError);
  },

  closeDefinition: function closeDefinition() {
    if (typeof this.childViews.definition !== 'undefined') {
      this.childViews.definition.remove();
    }
  },

  updateChildViews: function updateChildViews(context) {
    this.$definition = this.$definition || this.$el.find('#definition');
    switch (context.type) {
      case 'reg-section':
        this.model.get(context.id, {}).then(this.openRegFolders.bind(this));
        MainEvents.trigger('definition:carriedOver');

          // definition container is hidden when SxS opens
        if (this.$definition.is(':hidden')) {
          this.$definition.show();
        }

        break;
      case 'search':
        this.removeChildren();
        this.loaded();
        break;
      case 'diff':
        this.loaded();
        break;
      default:
        this.removeChildren();
        this.loaded();
    }

    this.removeLandingSidebar();
  },

    /* AJAX retrieved a sidebar. Replace the relevant portions of the
     * existing sidebar */
  openRegFolders: function openRegFolders(html) {
        // remove all except definition
    this.removeChildren('definition');

    this.$el.find('[data-cache-key=sidebar]').remove();
    this.$el.append(html);

        // new views to bind to new html
    this.childViews.sxs = new SxSList();
    this.loaded();
  },

  removeLandingSidebar: function removeLandingSidebar() {
    $('.landing-sidebar').hide();
  },

  insertDefinition: function insertDefinition(el) {
    this.closeExpandables();

    if (this.$el.definition.length === 0) {
            // if the page was loaded on the landing, search or 404 page,
            // it won't have the content sidebar template
      this.$el.prepend('<section id="definition"></section>');
      this.$el.definition = this.$el.find('#definition');
    }

    this.$el.definition.html(el);
  },

  closeExpandables: function closeExpandables() {
    this.$el.find('.expandable').each((i, folder) => {
      const $folder = $(folder);
      if ($folder.hasClass('open')) {
        this.toggleExpandable($folder);
      }
    });
  },

  toggleExpandable: function toggleExpandable(e) {
    let $expandable;

    if (typeof e.stopPropagation !== 'undefined') {
      e.stopPropagation();
      $expandable = $(e.currentTarget);
    } else {
      $expandable = e;
    }
    Helpers.toggleExpandable($expandable, 400);
  },

  removeChildren: function removeChildren(except) {
    const self = this;
    $.each(this.childViews, (key) => {
      if (!except || except !== key) {
        self.childViews[key].remove();
      }
    });
    /* Also remove any components of the sidebar which don't have a Backbone
     * view */
    this.$el.find('.regs-meta').remove();
  },

  loading: function loading() {
    this.$el.addClass('loading');
  },

  loaded: function loaded() {
    this.$el.removeClass('loading');
  },

    // when breakaway view loads
  hideChildren: function hideChildren() {
    this.loading();
  },
});

module.exports = SidebarView;
