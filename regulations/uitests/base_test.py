import os

from selenium import webdriver
from six.moves.urllib.parse import urlparse


ie_shorthand = {}
for idx in range(8, 12):
    capability = webdriver.DesiredCapabilities.INTERNETEXPLORER.copy()
    capability['version'] = str(idx)
    ie_shorthand['ie{0}'.format(idx)] = capability


class BaseTest():

    job_name = 'eRegs UI Test'

    def setUp(self):
        self.test_url = os.environ['UITESTS_URL']
        self.driver = (
            self.make_remote()
            if 'UITESTS_REMOTE' in os.environ
            else self.make_local()
        )
        self.driver.set_window_size(800, 600)
        self.driver.implicitly_wait(30)

    def make_local(self):
        attr = os.environ.get('UITESTS_LOCAL', 'PhantomJS')
        klass = getattr(webdriver, attr)
        if not isinstance(klass, type):
            raise TypeError(
                'Option {} did not resolve to a class'.format(attr))
        return klass()

    def make_remote(self):
        browser = os.environ['UITESTS_REMOTE']
        if browser in ie_shorthand:
            capabilities = ie_shorthand[browser].copy()
        else:
            capabilities = getattr(webdriver.DesiredCapabilities,
                                   browser.upper())
        capabilities['name'] = self.job_name
        if (os.environ.get('TRAVIS') and
                os.environ.get('TRAVIS_SECURE_ENV_VARS')):
            capabilities.update({
                'tunnel-identifier': os.environ['TRAVIS_JOB_NUMBER'],
                'build': os.environ['TRAVIS_BUILD_NUMBER'],
            })

        username = os.environ['SAUCE_USERNAME']
        key = os.environ['SAUCE_ACCESS_KEY']
        hub_url = "%s:%s" % (username, key)
        executor = "http://%s@ondemand.saucelabs.com:80/wd/hub" % hub_url
        driver = webdriver.Remote(desired_capabilities=capabilities,
                                  command_executor=executor)
        jobid = driver.session_id
        print("Sauce Labs job: https://saucelabs.com/jobs/%s" % jobid)
        return driver

    def urlparse(self, url=None):
        if url is None:
            url = self.driver.current_url
        return urlparse(url)

    def tearDown(self):
        self.driver.quit()
