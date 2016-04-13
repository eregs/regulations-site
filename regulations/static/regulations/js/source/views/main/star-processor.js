'use strict';

var $ = require('jquery');

/***
 * Functions to process the different types of "stars", indicators that text
 * can be expanded. Each accepts an $li which may need to be collapsed in
 * addition to an $expander to expand collapsed $li texts. Each method returns
 * an updated $expander.
 ***/
var StarProcessor = {
  none: function() { return null; },  /* No changes, no new expander */
  inline: function($li) {
    var $toShow = $li.find('.paragraph-text:first').hide();
    var $expander = $('<button>* * *</button>').insertBefore($toShow);
    var $paragraph = $expander.parent();

    $expander.click(function() {
      $expander.remove();
      $toShow.show();
    });

    /* "Collapsed" paragraphs have no immediate content, only subparagraphs.
     * However, we're now _adding_ content, so we need to fiddle with the
     * relevant classes and cleanup after ourselves when done */
    if ($paragraph.hasClass('collapsed')) {
      $paragraph.removeClass('collapsed');
      $expander.click(function() { $paragraph.addClass('collapsed'); });
    }
    return $expander;
  },
  full: function($li, $expander) {
    var $toShow = $li.children().hide();
    /* Generally, we want to reuse the existing expander */
    if (!$expander) {
      $expander = $('<button>STARS</button>').insertBefore($toShow);
      $expander.click(function() { $expander.remove(); });
    }

    $expander.click(function() { $toShow.show(); });
    return $expander;
  }
};

module.exports = StarProcessor;
