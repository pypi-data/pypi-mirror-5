import os
import requests
import time
from json import dumps, loads
from nose.plugins import Plugin
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from unittest2 import TestCase
from exceptions import TypeError #  , Exception
#from urllib2 import URLError

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# storing these at module level so they can be imported into scripts
BROWSER_LOCATION = None
BROWSER = None
BUILD = None
BROWSER_VERSION = None
OS = None
REMOTE_ADDRESS = None
REMOTE_PORT = None
TIMEOUT = None
SAUCE_USERNAME = None
SAUCE_APIKEY = None
SAVED_FILES_PATH = None

class NoseSelenium(Plugin):

    name = 'nose-selenium'
    score = 200
    status = {}

    def help(self):
        pass

    def _stringify_options(self, list):
        string = ", ".join(list)
        return "[" + string + "]"

    def options(self, parser, env=os.environ):

        Plugin.options(self, parser, env)
        valid_location_options = ['local', 'remote', 'grid', 'sauce']
        parser.add_option('--browser-location',
                          action='store',
                          choices=valid_location_options,
                          default=env.get('SELENIUM_BROWSER_LOCATION', 'local'),
                          dest='browser_location',
                          help="Run the browser in this location (default %default, options " +
                               self._stringify_options(valid_location_options) +
                               "). May be stored in environmental variable SELENIUM_BROWSER_LOCATION."
        )
        parser.add_option('--browser',
                          action='store',
                          default=env.get('SELENIUM_BROWSER', 'FIREFOX'),
                          dest='browser',
                          help="Run this type of browser (default %default). " +
                               "run --browser-help for a list of what browsers are available. " +
                               "May be stored in environmental variable SELENIUM_BROWSER."
        )
        parser.add_option('--browser-help',
                          action='store_true',
                          dest='browser_help',
                          help="Get a list of what OS, BROWSER, and BROWSER_VERSION combinations are available."
        )
        parser.add_option('--build',
                          action='store',
                          dest='build',
                          default=None,
                          metavar='str',
                          help='build identifier (for continuous integration). ' +
                               'Only used for sauce.'
        )
        parser.add_option('--browser-version',
                          action='store',
                          type='str',
                          default="",
                          dest='browser_version',
                          help='Run this version of the browser. ' +
                               '(default: %default implies latest.)'
        )
        parser.add_option('--os',
                          action='store',
                          dest='os',
                          default=None,
                          help="Run the browser on this operating system. " +
                               "(default: %default, required for grid or sauce)"
        )
        parser.add_option('--grid-address',
                          action='store',
                          dest='grid_address',
                          default=env.get('SELENIUM_GRID_ADDRESS', ''),
                          metavar='str',
                          help='host that selenium grid is listening on. ' +
                               '(default: %default) May be stored in environmental ' +
                               'variable SELENIUM_GRID_ADDRESS.'
        )
        parser.add_option('--grid-port',
                          action='store',
                          dest='grid_port',
                          type='int',
                          default=4444,
                          metavar='num',
                          help='port that selenium grid is listening on. ' +
                               '(default: %default)'
        )
        parser.add_option('--remote-address',
                          action='store',
                          dest='remote_address',
                          default=env.get('REMOTE_SELENIUM_ADDRESS', ''),
                          metavar='str',
                          help='host that remote selenium server is listening on. ' +
                               'May be stored in environmental variable REMOTE_SELENIUM_ADDRESS.'
        )
        parser.add_option('--remote-port',
                          action='store',
                          dest='remote_port',
                          type='int',
                          default=4444,
                          metavar='num',
                          help='port that remote selenium server is listening on. ' +
                               '(default: %default)'
        )
        parser.add_option('--timeout',
                          action='store',
                          type='int',
                          default=60,
                          metavar='num',
                          help='timeout (in seconds) for page loads, etc. ' +
                               '(default: %default)'
        )
        parser.add_option('--sauce-username',
                          action='store',
                          default=env.get('SAUCE_USERNAME', []),
                          dest='sauce_username',
                          metavar='str',
                          help='username for sauce labs account. ' +
                               'May be stored in environmental variable SAUCE_USERNAME.'
        )
        parser.add_option('--sauce-apikey',
                          action='store',
                          default=env.get('SAUCE_APIKEY', []),
                          dest='sauce_apikey',
                          metavar='str',
                          help='API Key for sauce labs account. ' +
                               'May be stored in environmental variable SAUCE_APIKEY.'
        )
        parser.add_option('--saved-files-storage',
                          action='store',
                          default=env.get('SAVED_FILES_PATH', ""),
                          dest='saved_files_storage',
                          metavar='PATH',
                          help='Full path to place to store screenshots and html dumps. ' +
                               'May be stored in environmental variable SAVED_FILES_PATH.'
        )

    def _check_validity(self, item, list, flag="--browser"):
        if item not in list:
            raise TypeError(
                "%s not in available options for %s: %s" %
                (item, flag, ", ".join(list))
            )

    def _get_sauce_options(self):
        # output from sauce labs
        # {
        #     "api_name": "firefox",
        #     "automation_backend": "webdriver",
        #     "long_name": "Firefox",
        #     "long_version": "19.0.",
        #     "os": "Linux",
        #     "preferred_version": "11",
        #     "scout": "webdriver",
        #     "short_version": "19"
        # },

        uri = 'http://saucelabs.com/rest/v1/info/browsers/webdriver'
        resp = loads(
            requests.get(uri, headers={ 'accepts': 'application/json'}).text)
        browser_hash = {}
        os_hash = {}
        combos = []
        for entry in resp:
            browser_hash.update({entry['api_name']: 1})
            os_hash.update({entry['os']: 1})
            combos.append("\t\t".join(
                [ entry['os'], entry['api_name'], entry['short_version']]))
        browsers = browser_hash.keys()
        oses = set(entry['os'] for entry in resp)
        return (browsers, oses, combos)

    def configure(self, options, conf):
        global BROWSER_LOCATION
        global BROWSER
        global BUILD
        global BROWSER_VERSION
        global OS
        global REMOTE_ADDRESS
        global REMOTE_PORT
        global TIMEOUT
        global SAUCE_USERNAME
        global SAUCE_APIKEY
        global SAVED_FILES_PATH


        Plugin.configure(self, options, conf)
        if self.enabled:


            valid_browsers_for_remote = [attr for attr in dir(webdriver.DesiredCapabilities) if not attr.startswith('__')]
            valid_browsers_for_local = ['FIREFOX', 'INTERNETEXPLORER', 'CHROME']

            # browser-help is a usage call
            if getattr(options, 'browser_help'):

                valid_browsers_for_sauce, valid_oses_for_sauce, combos = self._get_sauce_options()

                print("")
                print("Local Browsers:")
                print("---------------")
                print("\n".join(valid_browsers_for_local))
                print("")
                print("Potential Remote / Grid Browsers:")
                print("---------------------------------")
                print("\n".join(valid_browsers_for_remote))
                print("")
                print("Note: not all browsers available on all grids.")
                print("")
                print("Sauce Labs OS - Browser - Browser Version combinations:")
                print("-------------------------------------------------------")
                print("\t\t".join(['OS', 'BROWSER', 'BROWSER_VERSION']))
                print("\n".join(combos))
                exit(0)

            BROWSER_LOCATION = options.browser_location
            BROWSER = options.browser
            TIMEOUT = options.timeout
            BUILD = options.build
            OS = options.os
            SAVED_FILES_PATH = options.saved_files_storage

            # local
            if BROWSER_LOCATION == 'local':
                self._check_validity(BROWSER, valid_browsers_for_local)

            # sauce
            elif BROWSER_LOCATION == 'sauce':
                valid_browsers_for_sauce, valid_oses_for_sauce, combos = self._get_sauce_options()

                SAUCE_USERNAME = options.sauce_username
                SAUCE_APIKEY = options.sauce_apikey
                if not SAUCE_USERNAME or not SAUCE_APIKEY:
                    raise TypeError("'sauce' value for --browser-location "
                                    "requires --sauce-username and --sauce-apikey.")
                self._check_validity(BROWSER, valid_browsers_for_sauce)
                if not OS:
                    raise TypeError(
                        "'sauce' value for --browser-location requires the --os option.")
                self._check_validity(OS, valid_oses_for_sauce, flag="--os")

            # remote
            elif BROWSER_LOCATION == 'remote':
                REMOTE_PORT = options.remote_port
                REMOTE_ADDRESS = options.remote_address
                self._check_validity(BROWSER, valid_browsers_for_remote)
                if not REMOTE_ADDRESS:
                    raise TypeError(
                        "'remote' value for --browser-location requires --remote-address.")

            # grid
            elif BROWSER_LOCATION == 'grid':
                REMOTE_PORT = options.grid_port
                REMOTE_ADDRESS = options.grid_address
                self._check_validity(BROWSER, valid_browsers_for_remote)
                if not REMOTE_ADDRESS:
                    raise TypeError(
                        "'grid' value for --browser-location requires --grid-address.")
                if not OS:
                    raise TypeError(
                        "'grid' value for --browser-location requires the --os option.")
#               # XXX validate OS once grid API can answer the question which it supports


#    def finalize(self, result):
#        super(NoseSelenium, self).finalize(result)

class ScreenshotOnExceptionWebDriver(webdriver.Remote):


    def __init__(self, command_executor,
                 desired_capabilities=None, browser_profile=None, proxy=None):
        super(ScreenshotOnExceptionWebDriver, self).__init__(
                command_executor=command_executor,
                desired_capabilities=desired_capabilities,
                browser_profile=browser_profile,
                proxy=proxy
            )
        global SAVED_FILES_PATH
        if SAVED_FILES_PATH:
            os.system("mkdir -p %s" % SAVED_FILES_PATH)

    def execute(self, driver_command, params=None):
        try:
            return super(ScreenshotOnExceptionWebDriver,
                         self).execute(driver_command, params=params)
        except WebDriverException:
            global SAVED_FILES_PATH
            if SAVED_FILES_PATH:
                timestamp = repr(time.time()).replace('.', '')
                # save a screenshot
                screenshot_filename = SAVED_FILES_PATH + "/" + timestamp + ".png"
                super(ScreenshotOnExceptionWebDriver,
                      self).get_screenshot_as_file(screenshot_filename)
                logger.error("Screenshot saved to %s" % screenshot_filename)
                # save the html
                html_filename = SAVED_FILES_PATH + "/" + timestamp + ".html"
                html = super(ScreenshotOnExceptionWebDriver,self).page_source
                outfile = open(html_filename, 'w')
                outfile.write(html.encode('utf8', 'ignore'))
                outfile.close()
                logger.error("HTML saved to %s" % html_filename)
            raise


def build_webdriver(name="", tags=[], public=False):
    """Create and return the desired WebDriver instance."""
    global BROWSER_LOCATION
    global BROWSER
    global BUILD
    global BROWSER_VERSION
    global OS
    global REMOTE_ADDRESS
    global REMOTE_PORT
    global TIMEOUT
    global SAUCE_USERNAME
    global SAUCE_APIKEY

    wd = None

    if BROWSER_LOCATION == 'local':
        if BROWSER == 'FIREFOX':
            wd = webdriver.Firefox()
        elif BROWSER == 'CHROME':
            wd = webdriver.Chrome()
        elif BROWSER == 'INTERNETEXPLORER':
            wd = webdriver.Ie()
        else:
            raise TypeError(
                'WebDriver does not have a driver for local %s' % BROWSER)

    elif BROWSER_LOCATION == 'remote':
        capabilities = getattr(webdriver.DesiredCapabilities, BROWSER.upper())
        executor = 'http://%s:%s/wd/hub' % (REMOTE_ADDRESS, REMOTE_PORT)
        # try:
        wd = ScreenshotOnExceptionWebDriver(command_executor=executor,
                              desired_capabilities=capabilities)
        # except URLError:
        #     # print(" caught URLError ",)
        #     raise Exception(
        #         "Remote selenium server at %s:%s is not responding."
        #         % (REMOTE_ADDRESS, REMOTE_PORT))

    elif BROWSER_LOCATION == 'grid':
        capabilities = getattr(webdriver.DesiredCapabilities, BROWSER.upper())
        capabilities['version'] = BROWSER_VERSION
        capabilities['platform'] = OS.upper()
        executor = 'http://%s:%s/wd/hub' % (REMOTE_ADDRESS, REMOTE_PORT)
        # try:
        wd = ScreenshotOnExceptionWebDriver(command_executor=executor,
                              desired_capabilities=capabilities)
        # except URLError:
        #     # print(" caught URLError ",)
        #     raise Exception(
        #         "Selenium grid server at %s:%s is not responding."
        #         % (REMOTE_ADDRESS, REMOTE_PORT))

    elif BROWSER_LOCATION == 'sauce':
        capabilities = {
            'build': BUILD,
            'name': name,
            'tags': tags,
            'public': public,
            'restricted-public-info': not public,
            'platform': OS,
            'browserName': BROWSER,
            'version': BROWSER_VERSION,
        }
        executor = 'http://%s:%s@ondemand.saucelabs.com:80/wd/hub' % (SAUCE_USERNAME, SAUCE_APIKEY)
        wd = ScreenshotOnExceptionWebDriver(command_executor=executor,
                              desired_capabilities=capabilities)
    else:
        raise TypeError("browser location %s not found" % BROWSER_LOCATION)

    wd.implicitly_wait(TIMEOUT)
    # sometimes what goes out != what goes in, so log it
    logger.info("actual capabilities: %s" % wd.capabilities)
    return wd


class SeleniumTestCase(TestCase):

    def setUp(self):
        self.wd = build_webdriver()

    def tearDown(self):
        self.wd.quit()

