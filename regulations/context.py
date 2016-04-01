from six.moves.urllib_parse import urlencode

from django.conf import settings
from django.core.urlresolvers import reverse


def eregs_globals(request):
    env = 'source' if getattr(settings, 'JS_DEBUG', False) else 'built'
    prefix = reverse('regulation_landing_view', kwargs={'label_id': '9999'})
    prefix = prefix.replace('9999', '')
    analytics = getattr(settings, 'ANALYTICS', {})
    if 'DAP' in analytics:
        analytics['DAP']['DAP_URL_PARAMS'] = create_dap_url_params(
            analytics['DAP'])
    return {
        'EREGS_GLOBALS': {
            'ENV': env,
            'APP_PREFIX': prefix,
            'ANALYTICS': analytics,
        },
    }


def create_dap_url_params(dap_settings):
    """ Create the DAP url string to append to script tag """
    dap_params = {}
    if 'AGENCY' in dap_settings and dap_settings['AGENCY']:
        dap_params['agency'] = dap_settings['AGENCY']
        if 'SUBAGENCY' in dap_settings and dap_settings['SUBAGENCY']:
            dap_params['subagency'] = dap_settings['SUBAGENCY']

    return urlencode(dap_params)
