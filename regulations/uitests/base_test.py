import os
from selenium import webdriver


remote_configs = {
    'chrome': {
        'driver': webdriver.DesiredCapabilities.CHROME,
        'platform': 'LINUX',
        'version': '',
    },
    'ie11': {
        'driver': webdriver.DesiredCapabilities.INTERNETEXPLORER,
        'platform': 'Windows 10',
        'version': '11',
    }
}


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
        selenium_config = remote_configs[os.environ['UITESTS_REMOTE']]
        capabilities = selenium_config['driver']
        if (os.environ.get('TRAVIS')
                and os.environ.get('TRAVIS_SECURE_ENV_VARS')):
            capabilities.update({
                'tunnel-identifier': os.environ['TRAVIS_JOB_NUMBER'],
                'build': os.environ['TRAVIS_BUILD_NUMBER'],
            })

        username = os.environ['SAUCE_USERNAME']
        key = os.environ['SAUCE_ACCESS_KEY']
        capabilities['name'] = self.job_name
        capabilities['platform'] = selenium_config['platform']
        capabilities['version'] = selenium_config['version']
        hub_url = "%s:%s" % (username, key)
        executor = "http://%s@ondemand.saucelabs.com:80/wd/hub" % hub_url
        driver = webdriver.Remote(desired_capabilities=capabilities,
                                  command_executor=executor)
        jobid = driver.session_id
        print("Sauce Labs job: https://saucelabs.com/jobs/%s" % jobid)
        return driver

    def tearDown(self):
        self.driver.quit()
