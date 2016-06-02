var expect = require('chai').expect;
var jsdom = require('mocha-jsdom');

describe('Non-DOM Helper functions:', function() {
    'use strict';

    var $, Helpers;

    jsdom();

    before(function (){
        $ = require('jquery');
        Helpers = require('../../source/helpers');
    });

    it('findBaseSection should find base sections of any id', function() {
        expect(Helpers.findBaseSection('1234-2-a-1')).to.equal('1234-2');

        expect(Helpers.findBaseSection('I-1234-5')).to.equal('I-1234');

        expect(Helpers.findBaseSection('1234-C-1')).to.equal('1234-C');

        expect(Helpers.findBaseSection('123-4-Interp-5')).to.equal('123-4-Interp');

        expect(Helpers.findBaseSection('123-Appendices-Interp-4')).to.equal('123-Appendices-Interp');

        expect(Helpers.findBaseSection('123-Subpart-A-Interp-4')).to.equal('123-Subpart-A-Interp');

        expect(Helpers.findBaseSection('123-Subpart-Interp-4')).to.equal('123-Subpart-Interp');

        expect(Helpers.findBaseSection('123-Interp-h1')).to.equal('123-Interp-h1');

        expect(Helpers.findBaseSection('123')).to.equal('123');

        expect(Helpers.findBaseSection('123-A')).to.equal('123-A');
    });

    it('isSupplement should be able to tell if it\'s a supplement', function () {
        expect(Helpers.isSupplement('13-Interp')).isTrue;

        expect(Helpers.isSupplement('123-Appendices-Interp')).isTrue;

        expect(Helpers.isSupplement('87324-34-b-23-iv-H')).isFalse;

        expect(Helpers.isSupplement('50')).isFalse;

    });

    it('isAppendix should find Appendices', function () {
        expect(Helpers.isAppendix('13-Interp')).isFalse;

        expect(Helpers.isAppendix('123-Appendices-Interp')).isTrue;

        expect(Helpers.isAppendix('87324-34-b-23-iv-H')).isFalse;

        expect(Helpers.isAppendix('50')).isFalse;
    });

    it('formatSubpartLabel should format correctly', function(){

        expect(Helpers.formatSubpartLabel('123-Subpart-C')).to.equal('Subpart C');

        expect(Helpers.formatSubpartLabel('13-Interp')).to.equal('Subpart ');
    });
});

describe('parsePreambleId', function() {
    'use strict';

    var Helpers;
    before(function (){ Helpers = require('../../source/helpers'); });

    it('parses relevant fields from the id string', function() {
        expect(Helpers.parsePreambleId('2016_02749-preamble-2016_02749-I-A')).to.eql(
            {
                path: ['preamble', '2016_02749', 'I'],
                type: 'preamble',
                docId: '2016_02749',
                section: ['2016_02749', 'I'],
                hash: '2016_02749-I-A'
            });

        expect(Helpers.parsePreambleId('2016_02749-cfr-478-32-a-1')).to.eql(
            {
                path: ['preamble', '2016_02749', 'cfr_changes', '478-32'],
                type: 'cfr',
                docId: '2016_02749',
                section: ['478', '32'],
                hash: '478-32-a-1'
            });
    });

    it('does not add a hash for top-level sections', function() {
        expect(Helpers.parsePreambleId('2016_02749-preamble-2016_02749-I').hash).to.be.undefined;
        expect(Helpers.parsePreambleId('2016_02749-cfr-478-32').hash).to.be.undefined;
    });

});

describe('parsePreambleCitationId', function() {
    'use strict';

    var Helpers;
    before(function (){ Helpers = require('../../source/helpers'); });

    it('parses citation link correctly to section', function() {
        // link with only a hash
        expect(Helpers.parsePreambleCitationId('#0000_0000-III-D-4', 'preamble-section')).to.eql('0000_0000-preamble-0000_0000-III-D-4');

        expect(Helpers.parsePreambleCitationId('#2016_02749-I', 'preamble-section')).to.eql('2016_02749-preamble-2016_02749-I');

        expect(Helpers.parsePreambleCitationId('#0000_0000-III-F-6', 'preamble-section')).to.eql('0000_0000-preamble-0000_0000-III-F-6');

        // link with section before hash
        expect(Helpers.parsePreambleCitationId('III#0000_0000-III-D-4', 'preamble-section')).to.eql('0000_0000-preamble-0000_0000-III-D-4');

        expect(Helpers.parsePreambleCitationId('II#0000_0000-II-B', 'preamble-section')).to.eql('0000_0000-preamble-0000_0000-II-B');
    });
});

describe('Version Finder Helper Functions:', function() {
    'use strict';

    var $, Helpers;

    jsdom();

    var navMenu, navMenu_blank, section, section_blank, timeline, timeline_blank;

    before(function () {
        $ = require('jquery');
        Helpers = require('../../source/helpers');
    });

    it('should return version when "nav#toc" present on the element', function() {

        var tocTest = {
            toc: $('<nav id="toc" data-toc-version="nav-date"></nav>')
        };

        var sectionTest = {
            toc: $('<nav id="toc"></nav>'),
            regLandingPage: $('<section data-base-version="section-date"></section>')
        };

        var timelineTest = {
            toc: $('<nav id="toc"></nav>'),
            timelineList: $('<a id="timeline"><li class="current"><a class="stop-button" data-version="timeline-date"></a></li></a>')
        };

        expect(Helpers.findVersion(tocTest)).to.equal('nav-date');
        expect(Helpers.findVersion(sectionTest)).to.equal('section-date');
        expect(Helpers.findVersion(timelineTest)).to.equal('timeline-date');

        //Add a different date somewhere. It should grab the date in the Nav first.
        tocTest.regLandingPage = $('<section data-base-version="section-date"></section>');

        expect(Helpers.findVersion(tocTest)).to.not.equal('section-date');
    });

    it('should find version on section when "nav#toc" is not present', function() {

        var sectionTest = {
            toc: $('<nav id="toc"></nav>'),
            regLandingPage: $('<section data-base-version="section-date"></section>')
        };

        var timelineTest = {
            toc: $('<nav id="toc"></nav>'),
            regLandingPage: $('<section data-base-version="section-date"></section>'),
            timelineList: $('<a id="timeline"><li class="current"><a class="stop-button" data-version="timeline-date"></a></li></a>')
        };

        expect(Helpers.findVersion(sectionTest)).to.equal('section-date');
        expect(Helpers.findVersion(timelineTest)).to.not.equal('timeline-date');

    });

    it('should find version on timeline if version isn\'t available anywhere else', function() {

        var timelineTest = {
            toc: $('<nav id="toc"></nav>'),
            regLandingPage: $('<section data-base-version="section-date"></section>'),
            timelineList: $('<a id="timeline"><li class="current"><a class="stop-button" data-version="timeline-date"></a></li></a>')
        };

        // It searches for the stop button because of the diff version.
        var diffVersion = {
            timelineList: $('<a id="timeline"><li class="current"><a data-version="timeline-date"></a></li></a>')
        };

        expect(Helpers.findVersion(timelineTest)).to.not.equal('timeline-date');
        expect(Helpers.findVersion(diffVersion)).to.not.be.ok;
    });

    it('works with findDiffVersion', function() {

        var tocTest = {
            toc: $('<nav id="toc" data-toc-version="nav-date"></nav>'),
            diffToc: $('<div id="table-of-contents" data-from-version="diff-toc-date"></div>'),
            timelineList: $('<div id="timeline"><li class="current"><a class="version-link" data-version="version-link-date"></a></li></div>')
        };

        expect(Helpers.findDiffVersion(tocTest)).to.equal('diff-toc-date');

    });

    it('returns the right data when diffVersion = version', function(){
        var diffTest = {
            toc: $('<nav id="toc" data-toc-version="same-date"></nav>'),
            diffToc: $('<div id="table-of-contents" data-from-version="same-date"></div>'),
            timelineList: $('<div id="timeline"><li class="current"><a class="version-link" data-version="diff-date">Regulation</a></li></div>')
        };

        expect(Helpers.findDiffVersion(diffTest, 'same-date')).to.equal('diff-date');
        expect(Helpers.findDiffVersion(diffTest)).to.equal('diff-date');
    });

});
