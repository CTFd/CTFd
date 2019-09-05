from CTFd.config import TestingConfig
from tests.helpers import (
    create_ctfd,
    destroy_ctfd
)
from multiprocessing import Process
import time
import pytest


@pytest.fixture
def chrome_options(chrome_options):
    chrome_options.add_argument('headless')
    chrome_options.add_argument('no-sandbox')
    return chrome_options


@pytest.mark.element
def test_example_element(needle):
    class LiveTestingConfig(TestingConfig):
        SERVER_NAME = "localhost:5000"

    app = create_ctfd(config=LiveTestingConfig)

    server = Process(target=app.run, kwargs={'debug': True, 'threaded': True, 'host': "127.0.0.1", 'port': 5000})
    server.daemon = True
    server.start()
    time.sleep(3)

    needle.driver.get('http://localhost:5000/')
    needle.assert_screenshot('index')

    needle.driver.get('http://localhost:5000/login')
    needle.assert_screenshot('login')

    name = needle.driver.find_element_by_css_selector('input[name=name]')
    password = needle.driver.find_element_by_css_selector('input[name=password]')
    submit = needle.driver.find_element_by_css_selector('button[type=submit]')
    name.send_keys("admin")
    password.send_keys("password")
    submit.click()

    needle.driver.get('http://localhost:5000/scoreboard')
    time.sleep(1)
    needle.assert_screenshot('scoreboard')

    server.terminate()
    destroy_ctfd(app)
