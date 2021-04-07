from django.urls import path, register_converter

from regulations.views.reader import SubpartReaderView, SectionReaderView, PartReaderView
from regulations.views.goto import GoToRedirectView
from regulations.views.search import SearchView
from regulations.views.regulation_landing import RegulationLandingView
from regulations.views.homepage import HomepageView
from regulations import converters

register_converter(converters.NumericConverter, 'numeric')
register_converter(converters.SubpartConverter, 'subpart')
register_converter(converters.VersionConverter, 'version')

urlpatterns = [
    path('', HomepageView.as_view(), name='homepage'),
    path('<numeric:part>/', RegulationLandingView.as_view(), name="regulation_landing_view"),
    path('<numeric:part>/<version:version>/', PartReaderView.as_view(), name='reader_view'),
    path('<numeric:part>/<numeric:section>/<version:version>/', SectionReaderView.as_view(), name='reader_view'),
    path('<numeric:part>/<subpart:subpart>/<version:version>/', SubpartReaderView.as_view(), name="reader_view"),
    path('goto/', GoToRedirectView.as_view(), name='goto'),
    path('search/', SearchView.as_view(), name='search'),
]
