

const $ = require('jquery');

/**
 * Functions to process the different types of "stars", indicators that text
 * can be expanded. Each accepts an $li which may need to be collapsed in
 * addition to an $expander to expand collapsed $li texts. Each method returns
 * an updated $expander.
 */

const starContent = '<button class="show-more-context">&#9733; &nbsp;&nbsp; &#9733; &nbsp;&nbsp; &#9733; <span>Show more context</span> &#9733; &nbsp;&nbsp; &#9733; &nbsp;&nbsp; &#9733;</button>';

module.exports = {
  none: function none() { return null; },  /* No changes, no new expander */
  inline: function inline($li) {
    const $toShow = $li.find('.paragraph-text:first').hide();
    const $expander = $(starContent).insertBefore($toShow);
    const $paragraph = $expander.parent();

    $expander.click(() => {
      $expander.remove();
      $toShow.show();
    });

    /**
     * "Collapsed" paragraphs have no immediate content, only subparagraphs.
     * However, we're now _adding_ content, so we need to fiddle with the
     * relevant classes and cleanup after ourselves when done
     */
    if ($paragraph.hasClass('collapsed')) {
      $paragraph.removeClass('collapsed');
      $expander.click(() => { $paragraph.addClass('collapsed'); });
    }
    return $expander;
  },
  full: function full($li, expanderEl) {
    let $expander = expanderEl;
    let $toShow;
    /* Generally, we want to reuse the existing expander */
    if ($expander) {
      $toShow = $li.hide();
    } else {
      $toShow = $li.children().hide();
      $expander = $(starContent).insertBefore($toShow);
      $expander.click(() => { $expander.remove(); });
    }

    $expander.click(() => { $toShow.show(); });
    return $expander;
  },
};
