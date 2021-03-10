from django.urls import path, register_converter
from django.conf.urls import url

from regulations.url_caches import daily_cache, lt_cache
from regulations.views.about import about
from regulations.views.chrome_breakaway import ChromeSXSView
from regulations.views.chrome import (
    ChromeView,
    ChromeSearchView)
from regulations.views.diff import ChromeSectionDiffView
from regulations.views.diff import PartialSectionDiffView
from regulations.views.partial import PartialDefinitionView
from regulations.views.partial import PartialRegulationView
from regulations.views.reader import SubpartReaderView, SectionReaderView, PartReaderView
from regulations.views import partial_interp
from regulations.views.partial_search import PartialSearch
from regulations.views.partial_sxs import ParagraphSXSView
from regulations.views.preamble import (
    CFRChangesView, PreambleView, ChromePreambleSearchView
)
from regulations.views.goto import GoToRedirectView
from regulations.views.redirect import (
    diff_redirect,
    redirect_by_current_date,
    redirect_by_date,
    redirect_by_date_get
)
from regulations.views.sidebar import SideBarView
from regulations.views.universal_landing import universal
from regulations.views.regulation_landing import RegulationLandingView
from regulations.views import converters

# Reusable pattern matching constants to improve readability
match_version = match_notice = r'[-\d\w_]+'
match_section = r'[\d]+[-][\w]+'
match_paragraph = r'[-\w]+'
match_reg = r'[\d]+'
match_preamble = r'[\w]+'
match_paragraphs = r'[-\w]+(/[-\w]+)*'
match_year = r'\d{4}'
match_day = match_month = r'\d{2}'
match_interp = r'[-\w]+[-]Interp'
match_sub_interp = r'[\d]+-(Appendices|Subpart(-[A-Z]+)?)-Interp'

register_converter(converters.NumericConverter, 'numeric')
register_converter(converters.SubpartConverter, 'subpart')
register_converter(converters.VersionConverter, 'version')

urlpatterns = [
    # Index page
    # Example http://.../
    url(rf'^$', universal, name='universal_landing'),

    # About page
    # Example http://.../about
    url(rf'^about$', about, name='about'),

    # Redirect to version by date (by GET)
    # Example http://.../regulation_redirect/201-3-v
    url(rf'^regulation_redirect/(?P<label_id>{match_paragraph})$',
        redirect_by_date_get, name='redirect_by_date_get'),

    # Redirect to a diff based on GET params
    # Example http://.../diff_redirect/201-3/old_version?new_version=new
    url(rf'^diff_redirect/(?P<label_id>{match_section})/(?P<version>{match_version})$',
        diff_redirect, name='diff_redirect'),

    # A section by section paragraph with chrome
    # Example: http://.../sxs/201-2-g/2011-1738
    url(rf'^sxs/(?P<label_id>{match_paragraph})/(?P<notice_id>{match_notice})$',
        lt_cache(ChromeSXSView.as_view()), name='chrome_sxs_view'),

    # Search results for non-JS viewers
    # Example: http://.../search?q=term&version=2011-1738
    url(rf'^search(?:/cfr)?/(?P<label_id>{match_reg})$',
        ChromeSearchView.as_view(),
        name='chrome_search',
        kwargs={'doc_type': 'cfr'}),
    url(rf'^search/preamble/(?P<label_id>{match_preamble})$',
        ChromePreambleSearchView.as_view(),
        name='chrome_search_preamble',
        kwargs={'doc_type': 'preamble'}),

    # Diff view of a section for non-JS viewers (or book markers)
    # Example: http://.../diff/201-4/2011-1738/2013-10704
    url(rf'^diff/(?P<label_id>{match_section})/(?P<version>{match_version})/(?P<newer_version>{match_version})$',
        lt_cache(ChromeSectionDiffView.as_view()), name='chrome_section_diff_view'),
    url(rf'^preamble/(?P<doc_number>{match_paragraph})/cfr_changes/(?P<section>{match_paragraph})$',
        daily_cache(CFRChangesView.as_view()), name='cfr_changes'),
    url(rf'^preamble/(?P<paragraphs>{match_paragraphs})$',
        daily_cache(PreambleView.as_view()), name='chrome_preamble'),

    # Redirect to version by date
    # Example: http://.../201-3-v/1999/11/8
    url(rf'^(?P<label_id>{match_paragraph})/(?P<year>{match_year})/(?P<month>{match_month})/(?P<day>{match_day})$',
        redirect_by_date, name='redirect_by_date'),

    # Redirect to version by current date
    # Example: http://.../201-3-v/CURRENT
    url(rf'^(?P<label_id>{match_paragraph})/CURRENT$',
        redirect_by_current_date, name='redirect_by_current_date'),

    path('<numeric:part>/<version:version>/', PartReaderView.as_view(), name='part_reader_view'),
    path('<numeric:part>/<numeric:section>/<version:version>/', SectionReaderView.as_view(), name='section_reader_view'),
    path('<numeric:part>/<subpart:subpart>/<version:version>/', SubpartReaderView.as_view(), name="subpart_reader_view"),

    path('goto/', GoToRedirectView.as_view(), name='goto'),
    # Interpretation of a section/paragraph or appendix
    # Example: http://.../201-4-Interp/2013-10704
    url(rf'^(?P<label_id>{match_interp})/(?P<version>{match_version})$',
        lt_cache(ChromeView.as_view(partial_class=partial_interp.PartialInterpView)),
        name='chrome_interp_view'),

    # A regulation landing page
    # Example: http://.../201
    path('<part>/', RegulationLandingView.as_view(), name="regulation_landing_view"),

    # Load just the sidebar
    # Example: http://.../partial/sidebar/201-2/2013-10704
    url(rf'^partial/sidebar/(?P<label_id>{match_paragraph})/(?P<version>{match_version})$',
        SideBarView.as_view(), name='sidebar'),

    # Load just search results
    url(rf'^partial/search(?:/cfr)?/(?P<label_id>{match_reg})$',
        PartialSearch.as_view(),
        name='partial_search',
        kwargs={'doc_type': 'cfr'}),
    url(rf'^partial/search/preamble/(?P<label_id>{match_preamble})$',
        PartialSearch.as_view(),
        name='partial_search',
        kwargs={'doc_type': 'preamble'}),

    # A diff view of a section (without chrome)
    url(rf'^partial/diff/(?P<label_id>{match_section})/(?P<version>{match_version})/(?P<newer_version>{match_version})$',
        lt_cache(PartialSectionDiffView.as_view()), name='partial_section_diff_view'),

    # A section by section paragraph (without chrome)
    # Example: http://.../partial/sxs/201-2-g/2011-1738
    url(rf'^partial/sxs/(?P<label_id>{match_paragraph})/(?P<notice_id>{match_notice})$',
        lt_cache(ParagraphSXSView.as_view()), name='paragraph_sxs_view'),

    # A definition templated to be displayed in the sidebar (without chrome)
    # Example: http://.../partial/definition/201-2-g/2011-1738
    url(rf'^partial/definition/(?P<label_id>{match_paragraph})/(?P<version>{match_version})$',
        lt_cache(PartialDefinitionView.as_view()), name='partial_definition_view'),

    # An interpretation of a section/paragraph or appendix without chrome.
    # Example: http://.../partial/201-2-Interp/2013-10704
    url(rf'^partial/(?P<label_id>{match_interp})/(?P<version>{match_version})$',
        lt_cache(partial_interp.PartialInterpView.as_view()), name='partial_interp_view'),

    # The whole regulation without chrome; not too useful; added for symmetry
    # Example: http://.../partial/201/2013-10704
    url(rf'^partial/(?P<label_id>{match_reg})/(?P<version>{match_version})$',
        lt_cache(PartialRegulationView.as_view()), name='partial_regulation_view'),
]
