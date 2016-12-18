// Defines some globally useful helper functions
'use strict';
var $ = require('jquery');
var _ = require('underscore');
var markerlessRE = /p\d+/;

// indexOf polyfill
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/indexOf
// TODO this may make sense to move elsewhere
if (!Array.prototype.indexOf) {
  Array.prototype.indexOf = function (searchElement, fromIndex) {
    if ( this === undefined || this === null ) {
      throw new TypeError( '"this" is null or not defined' );
    }

    var length = this.length >>> 0; // Hack to convert object.length to a UInt32

    fromIndex = +fromIndex || 0;

    if (Math.abs(fromIndex) === Infinity) {
      fromIndex = 0;
    }

    if (fromIndex < 0) {
      fromIndex += length;
      if (fromIndex < 0) {
        fromIndex = 0;
      }
    }

    for (;fromIndex < length; fromIndex++) {
      if (this[fromIndex] === searchElement) {
        return fromIndex;
      }
    }

    return -1;
  };
}

module.exports = {
    // Finds parent-most reg paragraph
    findBaseSection: function(id) {
        var parts, interpIndex;

        if (id.indexOf('-') !== -1) {
            parts = id.split('-');
        } else {
            return id;
        }

        // if what has been passed in is a base section already
        // catches:
        // 123
        // 123-1
        // 123-A
        // 123-Interp
        if (parts.length <= 2) {
            return id;
        }

        interpIndex = parts.indexOf('Interp');

        if (interpIndex !== -1) {
            // catches 123-Interp-h1
            if (parts[1] === 'Interp') {
                return id;
            } else {
                // catches:
                // 123-4-Interp
                // 123-4-Interp-5
                // 123-Subpart-Interp
                // 123-Subpart-A-Interp
                // 123-Subpart-Interp-4
                // 123-Subpart-A-Interp-4
                // 123-Appendices-Interp
                // 123-Appendices-Interp-4
                return parts.slice(0, interpIndex + 1).join('-');
            }
        }

        // catches:
        // 123-4-*
        // 123-A-*
        return parts[0] + '-' + parts[1];
    },

    // Unpaired this function from the DOM to make
    // it more testable and flexible. Look at resources.js
    // to add places to look for version elements.
    // To call: `findVersion(Resources.versionElements)`

    // -- old message --
    // these next two are a little desperate and heavy handed
    // the next step, if the app were going to do more
    // interesting things, is to introduce the concept of reg
    // version and maybe effective dates to the architecture
    // at that time, this should be removed
    findVersion: function(versionElements) {
      return $(versionElements.toc).attr('data-toc-version') ||
                  $(versionElements.regLandingPage).attr('data-base-version')||
                  $(versionElements.timelineList).find('.stop-button').attr('data-version');
                    // includes .stop-button to be sure its not
                    // the comparison version in diff mode
    },

    // returns newer version. findVersion will return base version
    findDiffVersion: function(versionElements, currentVersion) {
        var version;
        currentVersion = currentVersion || this.findVersion(versionElements);
        version = $(versionElements.diffToc).attr('data-from-version');
        if (!version || version === currentVersion) {
            if ($(versionElements.timelineList).find('.version-link').attr('data-version') !== currentVersion) {
                version = $(versionElements.timelineList).find('.version-link').attr('data-version');
            }
        }

        return version;
    },

    isSupplement: function(id) {
        var parts;

        if (typeof id !== 'undefined') {
            parts = _.compact(id.split('-'));
            if (parts.length < 2) {
                return false;
            }

            if (parts[1].toLowerCase() === 'interp') {
                return true;
            }
        }

        return false;
    },

    isAppendix: function(id) {
        var parts;

        if (typeof id !== 'undefined') {
            parts = _.compact(id.split('-'));
            if (parts.length < 2) {
                return false;
            }

            if (isNaN(parts[1].substr(0, 1)) && parts[1].toLowerCase() !== 'interp') {
                return true;
            }
        }

        return false;
    },

    formatSubpartLabel: function(id) {
        // accepts 123-Subpart-C
        var parts = id.split('-'),
            label = 'Subpart ';
        if (isNaN(parts[0]) === false && parts[1] === 'Subpart') {
            label += parts[2];
        }

        return label;
    },

    // accepts to params:
    // element to be expanded
    // animation duration
    toggleExpandable: function($expandable, dur) {
        $expandable.toggleClass('open')
          .next('.chunk').slideToggle(dur);
    },

    /**
     * Parse a preamble section ID.
     * @param {string} id Preamble section ID
     * @see unittests for example usage
     */
    parsePreambleId: function(id) {
      var parts = id.split('-');
      var docId = parts.shift();
      var type = parts.shift();
      var path = ['preamble', docId];
      var section;
      if (type === 'preamble') {
        // Note: Document ID appears twice in preamble IDs
        // TODO: Standardize IDs and drop the `slice`
        path = path.concat(parts.slice(1, 2));
        section = [docId].concat(parts.slice(1, 2));
      } else if (type === 'cfr') {
        // Sections for CFR changes include the two first parts; the ID
        // 478-32-p243 maps to the section 478-32
        path = path.concat(['cfr_changes', parts.slice(0, 2).join('-')]);
        section = parts.slice(0, 2);
      }
      var parsed = {
        path: path,
        type: type,
        docId: docId,
        section: section,
      };
      /**
       * If linking to the top-level, we don't need a hash. Otherwise, link to
       * the beginning of the associated subsection
       **/
      if (parts.length > 2) {
        parsed.hash = parts.join('-');
      }
      return parsed;
    },

    /**
     * Parse the citation link hash to open the correct section.
     * @param {string} hash - the href link target section
     * @param {string} type - expecting 'preamble-section' from preamble-view.js options.type
     *
     * Example internal citation link:
     * <a href="#0000_0000-III-D-4" class="citation internal" data-section-id="0000_0000-III">III.D.4</a>
     * take href link and create a string "0000_0000-preamble-0000_0000-III-D-4"
     * to pass to 'section:open' event to load the linked section
     *
     * @see unittests
     */
    parsePreambleCitationId: function(hash, type) {
      // only grab the section info after #
      var section = hash.substring(hash.indexOf('#') + 1);
      var parts = section.split('-');
      var docId = parts.shift();

      if (type === 'preamble-section') {
        type = 'preamble';
      } else {
        type = 'cfr';
      }

      return [docId, type, section].join('-');
    },
};
