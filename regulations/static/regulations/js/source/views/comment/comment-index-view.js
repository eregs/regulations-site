import storage from '../../redux/storage';
import { locationActiveEvt } from '../../redux/locationReduce';
import { paneActiveEvt } from '../../redux/paneReduce';

const $ = require('jquery');
const _ = require('underscore');
const Backbone = require('backbone');

Backbone.$ = $;

const MainEvents = require('../../events/main-events');
const CommentEvents = require('../../events/comment-events');
const comments = require('../../collections/comment-collection');

function getOptions(elm) {
  const $elm = $(elm).closest('.comment-index-item');
  return {
    section: $elm.data('comment-section'),
    tocId: $elm.data('comment-toc-section'),
    label: $elm.data('comment-label'),
  };
}

module.exports = Backbone.CommentIndexView = Backbone.View.extend({
  events: {
    'click .comment-index-edit': 'editComment',
    'click .comment-index-clear': 'clearComment',
  },

  initialize: function initialize(options) {
    this.docId = options.docId;
    this.template = _.template($('#comment-index-template').html());
    this.$index = this.$el.find('.comment-index-items');
    this.$commentIndexReview = this.$el.find('.comment-index-review');

    this.listenTo(comments, 'add remove', this.render);

    this.render();
  },

  render: function render() {
    const commentData = comments.toJSON({ docId: this.docId });

    const html = this.template({ comments: commentData });
    this.$index.html(html);

    if (commentData.length) {
      this.$commentIndexReview.show();
    } else {
      this.$commentIndexReview.hide();
    }
  },

  editComment: function editComment(e) {
    const options = _.extend({ mode: 'write' }, getOptions(e.target));
    const type = options.section.split('-')[1];
    storage().dispatch(locationActiveEvt(options.tocId));
    storage().dispatch(paneActiveEvt(type === 'preamble' ? 'table-of-contents' : 'table-of-contents-secondary'));
    MainEvents.trigger('section:open', options.section, options, 'preamble-section');
    CommentEvents.trigger('comment:writeTabOpen');
  },

  clearComment: function clearComment(e) {
    const options = getOptions(e.target);
    const comment = comments.get(options.section);
    if (comment) {
      comment.destroy();
    }
  },
});
