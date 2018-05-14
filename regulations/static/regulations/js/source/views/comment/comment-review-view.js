import { paneActiveEvt } from '../../redux/paneReduce';
import storage from '../../redux/storage';

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');

Backbone.$ = $;

const MainEvents = require('../../events/main-events');
const CommentEvents = require('../../events/comment-events');
const comments = require('../../collections/comment-collection');

function selfOrChild($root, selector) {
  return $root.is(selector) ? $root : $root.find(selector);
}

function toggleInput($container, enabled) {
  $container.toggle(enabled);
  selfOrChild($container, 'input, select').prop('disabled', !enabled);
}

const CommentReviewView = Backbone.View.extend({
  events: {
    'click .edit-comment': 'editComment',
    'click .preview-button': 'preview',
    'change #agree': 'toggleSubmit',
  },

  initialize: function initialize(options) {
    Backbone.View.prototype.setElement.call(this, `#${options.id}`);

    this.$content = this.$el.find('.comment-review-items');

    this.docId = this.$el.data('doc-id');
    this.template = _.template($('#comment-template').html());

    this.previewLoading = false;

    storage().dispatch(paneActiveEvt('table-of-contents'));

    this.render();
  },

  findElms: function findElms() {
    this.$form = this.$el.find('form');
    this.$submit = this.$el.find('.submit-button');
    this.$agree = this.$el.find('#agree');
  },

  editComment: function editComment(e) {
    const section = $(e.target).closest('li').data('section');
    const label = $(e.target).closest('li').find('.comment-section-label').text();
    const options = { id: section, section, label, mode: 'write' };

    $('#content-body').removeClass('comment-review-wrapper');

    MainEvents.trigger('section:open', section, options, 'preamble-section');
    CommentEvents.trigger('comment:writeTabOpen');
  },

  render: function render() {
    const commentData = comments.toJSON({ docId: this.docId });
    const html = this.template({
      comments: commentData,
      previewLoading: this.previewLoading,
    });

    this.$content.html(html);
    this.findElms();

    this.toggleSubmit();

    this.initTabs();
    this.initDependencies();

    this.$form.find('[name="comments"]').val(JSON.stringify(commentData));

    // hide toggle elements
    this.$el.find('.toggle .collapsible').attr('aria-hidden', 'true').hide();
    this.$el.find('.toggle .toggle-button-close').attr('aria-hidden', 'true').hide();

    CommentEvents.trigger('comment:writeTabOpen');
  },

  initTabs: function initTabs() {
    const self = this;
    function updateTabs(tab, tabSet) {
      const tabSelector = `[data-tab="${tab}"]`;
      const setSelector = `[data-tab-set="${tabSet}"]`;
      self.$el.find(setSelector).removeClass('current');
      self.$el.find(setSelector + tabSelector).addClass('current');
      self.$el.find(`${setSelector}[data-tabs]`).each((idx, elm) => {
        const $elm = $(elm);
        const tabs = $elm.data('tabs');
        if (tabs.indexOf(tab) !== -1) {
          $elm.show();
        } else {
          $elm.hide();
        }
      });
    }

    const $tabs = self.$el.find('[data-tab]');
    updateTabs($tabs.data('tab'), $tabs.data('tab-set'));

    $tabs.on('click', function click(e) {
      const $tab = $(this);

      e.preventDefault();

      updateTabs($tab.data('tab'), $tab.data('tab-set'));
    });
  },

  /**
   * The regs.gov field definitions include compound fields in the sense that
   * one select filters the options of another. When the first select leads to
   * _no_ options available in the second, we need to display a "write-in".
   **/
  initDependencies: function initDependencies() {
    const self = this;
    self.$el.find('[data-depends-on]').each((idx, elm) => {
      const $elm = $(elm);
      const $select = selfOrChild($elm, 'select');
      const $dependsOn = self.$el.find(`[name="${$elm.data('depends-on')}"]`);
      const $options = $select.find('option[value]').detach().clone();
      const $writeIn = self.$el.find(`[data-writein-for="${$select.prop('id')}"]`);
      function updateOptions(value) {
        $select.find('option[value]').remove();
        let optionsCount = 0;
        const optionsToShow = [];
        $options.each((innerIdx, option) => {
          const depVal = option.getAttribute('data-dependency');
          if (depVal === value) {
            optionsCount += 1;
          }
          if (depVal === value || depVal === '_all') {
            optionsToShow.push(option);
          }
        });
        toggleInput($writeIn, optionsCount === 0);
        toggleInput($elm, optionsCount > 0);
        $select.append(optionsToShow);
        $select.val(null);
      }
      updateOptions($dependsOn.val());
      $dependsOn.on('change', function change() {
        updateOptions($(this).val());
      });
    });
  },

  preview: function preview(e) {
    e.preventDefault();

    const $xhr = $.ajax({
      type: 'POST',
      url: `${window.APP_PREFIX}comments/preview`,
      data: JSON.stringify({
        assembled_comment: comments.toJSON({ docId: this.docId }),
      }),
      contentType: 'application/json',
      dataType: 'json',
    });
    $xhr.then(this.previewSuccess.bind(this), this.previewError.bind(this));
    this.previewLoading = true;
    this.render();
  },

  previewSuccess: function previewSuccess(resp) {
    window.location = resp.url;
    this.previewLoading = false;
    this.render();
  },

  previewError: function previewError() {
    this.previewLoading = false;
    this.render();

    this.$el.find('.download-comment').find('.details').after('<div class="error">There was an error in building the PDF.</div>');
  },

  toggleSubmit: function toggleSubmit() {
    if (this.$agree.length) {
      this.$submit.prop('disabled', !this.$agree.prop('checked'));
    }
  },
});

module.exports = CommentReviewView;
