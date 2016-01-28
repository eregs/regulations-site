# vim: set fileencoding=utf-8
from unittest import TestCase
from regulations.generator.link_flattener import flatten_links


class LinkFlattenerTest(TestCase):
    def test_no_links(self):
        self.assertEqual("foo", flatten_links("foo"))

    def test_single_link(self):
        self.assertEqual(
            "<a href=foo> Fee Fie Foe </a>",
            flatten_links("<a href=foo> Fee Fie Foe </a>"))

    def test_unembedded_links(self):
        self.assertEqual(
            "<a href=foo> Fee </a> Fie <a href=bar> Foe </a>",
            flatten_links("<a href=foo> Fee </a> Fie <a href=bar> Foe </a>"))

    def test_embedded_link(self):
        self.assertEqual(
            "<a href=foo> Fee  Fie  Foe </a>",
            flatten_links("<a href=foo> Fee <a href=bar> Fie </a> Foe </a>"))

    def test_multiple_serial_embedded_links(self):
        self.assertEqual(
            "<a href=foo>FeeFieFoe</a>",
            flatten_links(
                "<a href=foo>Fee<a href=bar>Fie</a><a href=baz>Foe</a></a>")
        )

    def test_multiple_level_embedded_links(self):
        self.assertEqual(
            '<a href="1">A B C D E</a>',
            flatten_links(
                '<a href="1">A <a href="2">B <a href="3">C</a> D</a> E</a>')
        )

    def test_real_world_example(self):
        original = """
<span class="stripped-marker">a.</span><span class="paragraph-marker">(a)
</span> All of those items on <a href="/447-11/2015-12992#447-11-p3367907674"
class="citation definition" data-definition="447-11-p3367907674"
data-defined-term="the u.s. munitions import list">the U.S. Munitions Import
List</a> (see \xa7&nbsp;<a href="/447-21/2015-12992#447-21" class="citation
internal" data-section-id="447-21">447.21</a>) which are \u201c
<a href="/447-11/2015-12992#447-11-p21112113" class="citation definition"
data-definition="447-11-p21112113" data-defined-term="firearms">firearms</a>
\u201d or \u201cammunition\u201d as defined in 18
<a href="/447-21/2015-12992#447-21-p4-p67-c" class="citation definition"
data-definition="447-21-p4-p67-c" data-defined-term="u">U</a>.S.
<a href="/447-21/2015-12992#447-21-p4-p67-a" class="citation definition"
data-definition="447-21-p4-p67-a" data-defined-term="c">C</a>. 921(a) are
subject to the interstate and foreign commerce controls contained in Chapter
44 of Title 18 <a href="/447-21/2015-12992#447-21-p4-p67-c"
class="citation definition" data-definition="447-21-p4-p67-c"
data-defined-term="u">U</a>.S.<a href="/447-21/2015-12992#447-21-p4-p67-a"
class="citation definition" data-definition="447-21-p4-p67-a"
data-defined-term="c">C</a>. and <a href="http://api.fdsys.gov/link?
titlenum=27&partnum=478&collection=cfr&year=mostrecent"
class="citation external" target="_blank">27
<a href="/447-11/2015-12992#447-11-p3520592195" class="citation definition"
data-definition="447-11-p3520592195" data-defined-term="cfr">CFR</a> Part 478
</a> and if they are \u201c<a href="/447-11/2015-12992#447-11-p21112113"
class="citation definition" data-definition="447-11-p21112113"
data-defined-term="firearms">firearms</a>\u201d within the definition set out
in 26 <a href="/447-21/2015-12992#447-21-p4-p67-c" class="citation definition"
data-definition="447-21-p4-p67-c" data-defined-term="u">U</a>.S.
<a href="/447-21/2015-12992#447-21-p4-p67-a" class="citation definition"
data-definition="447-21-p4-p67-a" data-defined-term="c">C</a>. 5845(a) are
also subject to the provisions of <a href="http://api.fdsys.gov/link?
titlenum=27&partnum=479&collection=cfr&year=mostrecent"
class="citation external" target="_blank">27
<a href="/447-11/2015-12992#447-11-p3520592195" class="citation definition"
data-definition="447-11-p3520592195" data-defined-term="cfr">CFR</a> Part 479
</a>. Any <a href="/447-11/2015-12992#447-11-p3550103376"
class="citation definition" data-definition="447-11-p3550103376"
data-defined-term="person">person</a> engaged in the business of importing
<a href="/447-11/2015-12992#447-11-p21112113" class="citation definition"
data-definition="447-11-p21112113" data-defined-term="firearms">firearms</a>
or ammunition as defined in 18 <a href="/447-21/2015-12992#447-21-p4-p67-c"
class="citation definition" data-definition="447-21-p4-p67-c"
data-defined-term="u">U</a>.S.<a href="/447-21/2015-12992#447-21-p4-p67-a"
class="citation definition" data-definition="447-21-p4-p67-a"
data-defined-term="c">C</a>. 921(a) must obtain a
<a href="/447-11/2015-12992#447-11-p3473882945" class="citation definition"
data-definition="447-11-p3473882945" data-defined-term="license">license</a>
under the provisions of <a href="http://api.fdsys.gov/link?
titlenum=27&partnum=478&collection=cfr&year=mostrecent"
class="citation external" target="_blank">27
<a href="/447-11/2015-12992#447-11-p3520592195" class="citation definition"
data-definition="447-11-p3520592195" data-defined-term="cfr">CFR</a> Part 478
</a>, and if he <a href="/447-11/2015-12992#447-11-p3984137023"
class="citation definition" data-definition="447-11-p3984137023"
data-defined-term="import">imports</a>
<a href="/447-11/2015-12992#447-11-p21112113" class="citation definition"
data-definition="447-11-p21112113" data-defined-term="firearms">firearms</a>
which fall within the definition of 26
<a href="/447-21/2015-12992#447-21-p4-p67-c" class="citation definition"
data-definition="447-21-p4-p67-c" data-defined-term="u">U</a>.S.
<a href="/447-21/2015-12992#447-21-p4-p67-a" class="citation definition"
data-definition="447-21-p4-p67-a" data-defined-term="c">C</a>. 5845(a) must
also register and pay special tax pursuant to the provisions of
<a href="http://api.fdsys.gov/link?titlenum=27&partnum=479&collection=cfr
&year=mostrecent" class="citation external" target="_blank">27
<a href="/447-11/2015-12992#447-11-p3520592195" class="citation definition"
data-definition="447-11-p3520592195" data-defined-term="cfr">CFR</a> Part 479
</a>. Such licensing, registration and special tax requirements are in
addition to registration under subpart D of this part.
"""
        expected = """
<span class="stripped-marker">a.</span><span class="paragraph-marker">(a)
</span> All of those items on <a href="/447-11/2015-12992#447-11-p3367907674"
class="citation definition" data-definition="447-11-p3367907674"
data-defined-term="the u.s. munitions import list">the U.S. Munitions Import
List</a> (see \xa7&nbsp;<a href="/447-21/2015-12992#447-21" class="citation
internal" data-section-id="447-21">447.21</a>) which are \u201c
<a href="/447-11/2015-12992#447-11-p21112113" class="citation definition"
data-definition="447-11-p21112113" data-defined-term="firearms">firearms</a>
\u201d or \u201cammunition\u201d as defined in 18
<a href="/447-21/2015-12992#447-21-p4-p67-c" class="citation definition"
data-definition="447-21-p4-p67-c" data-defined-term="u">U</a>.S.
<a href="/447-21/2015-12992#447-21-p4-p67-a" class="citation definition"
data-definition="447-21-p4-p67-a" data-defined-term="c">C</a>. 921(a) are
subject to the interstate and foreign commerce controls contained in Chapter
44 of Title 18 <a href="/447-21/2015-12992#447-21-p4-p67-c"
class="citation definition" data-definition="447-21-p4-p67-c"
data-defined-term="u">U</a>.S.<a href="/447-21/2015-12992#447-21-p4-p67-a"
class="citation definition" data-definition="447-21-p4-p67-a"
data-defined-term="c">C</a>. and <a href="http://api.fdsys.gov/link?
titlenum=27&partnum=478&collection=cfr&year=mostrecent"
class="citation external" target="_blank">27
CFR Part 478
</a> and if they are \u201c<a href="/447-11/2015-12992#447-11-p21112113"
class="citation definition" data-definition="447-11-p21112113"
data-defined-term="firearms">firearms</a>\u201d within the definition set out
in 26 <a href="/447-21/2015-12992#447-21-p4-p67-c" class="citation definition"
data-definition="447-21-p4-p67-c" data-defined-term="u">U</a>.S.
<a href="/447-21/2015-12992#447-21-p4-p67-a" class="citation definition"
data-definition="447-21-p4-p67-a" data-defined-term="c">C</a>. 5845(a) are
also subject to the provisions of <a href="http://api.fdsys.gov/link?
titlenum=27&partnum=479&collection=cfr&year=mostrecent"
class="citation external" target="_blank">27
CFR Part 479
</a>. Any <a href="/447-11/2015-12992#447-11-p3550103376"
class="citation definition" data-definition="447-11-p3550103376"
data-defined-term="person">person</a> engaged in the business of importing
<a href="/447-11/2015-12992#447-11-p21112113" class="citation definition"
data-definition="447-11-p21112113" data-defined-term="firearms">firearms</a>
or ammunition as defined in 18 <a href="/447-21/2015-12992#447-21-p4-p67-c"
class="citation definition" data-definition="447-21-p4-p67-c"
data-defined-term="u">U</a>.S.<a href="/447-21/2015-12992#447-21-p4-p67-a"
class="citation definition" data-definition="447-21-p4-p67-a"
data-defined-term="c">C</a>. 921(a) must obtain a
<a href="/447-11/2015-12992#447-11-p3473882945" class="citation definition"
data-definition="447-11-p3473882945" data-defined-term="license">license</a>
under the provisions of <a href="http://api.fdsys.gov/link?
titlenum=27&partnum=478&collection=cfr&year=mostrecent"
class="citation external" target="_blank">27
CFR Part 478
</a>, and if he <a href="/447-11/2015-12992#447-11-p3984137023"
class="citation definition" data-definition="447-11-p3984137023"
data-defined-term="import">imports</a>
<a href="/447-11/2015-12992#447-11-p21112113" class="citation definition"
data-definition="447-11-p21112113" data-defined-term="firearms">firearms</a>
which fall within the definition of 26
<a href="/447-21/2015-12992#447-21-p4-p67-c" class="citation definition"
data-definition="447-21-p4-p67-c" data-defined-term="u">U</a>.S.
<a href="/447-21/2015-12992#447-21-p4-p67-a" class="citation definition"
data-definition="447-21-p4-p67-a" data-defined-term="c">C</a>. 5845(a) must
also register and pay special tax pursuant to the provisions of
<a href="http://api.fdsys.gov/link?titlenum=27&partnum=479&collection=cfr
&year=mostrecent" class="citation external" target="_blank">27
CFR Part 479
</a>. Such licensing, registration and special tax requirements are in
addition to registration under subpart D of this part.
"""
        self.assertEqual(expected, flatten_links(original))
