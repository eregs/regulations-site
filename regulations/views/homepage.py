from datetime import datetime
import logging

from django.views.generic.base import TemplateView
from requests import HTTPError

from regulations.views import utils
from regulations.generator import versions


logger = logging.getLogger(__name__)


def get_regulations_list(all_versions):
    regs = []
    reg_parts = sorted(all_versions.keys(), key=utils.make_sortable)

    for part in reg_parts:
        version = get_current_version(all_versions[part])
        if version is not None:
            reg_meta = utils.regulation_meta(part, version)
            first_section = utils.first_section(part, version)
            amendments = filter_future_amendments(all_versions.get(part, None))

            reg = {
                'part': part,
                'meta': reg_meta,
                'reg_first_section': first_section,
                'amendments': amendments
            }

            regs.append(reg)
    return regs


def get_current_version(versions):
    today = datetime.today()
    for version in versions:
        if version['by_date'] <= today:
            return version['version']
    return None


def filter_future_amendments(versions):
    today = datetime.today()
    amendments = [v for v in versions if v['by_date'] > today]
    amendments.sort(key=lambda v: v['by_date'])
    return amendments


class HomepageView(TemplateView):

    template_name = 'regulations/homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        c = {}
        try:
            all_versions = versions.fetch_regulations_and_future_versions()
            regs = get_regulations_list(all_versions)
            c = {
                'regulations': regs,
                'cfr_title_text': regs[0]['meta']['cfr_title_text'],
                'cfr_title_number': utils.to_roman(regs[0]['meta']['cfr_title_number']),
                'cfr_titleno_arabic': regs[0]['meta']['cfr_title_number'],
            }
        except HTTPError:
            logger.warning("NOTE: eRegs homepage loaded without any stored regulations.")

        return {**context, **c}
