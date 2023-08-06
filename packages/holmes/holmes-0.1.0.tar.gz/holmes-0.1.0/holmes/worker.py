#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import logging

from ujson import dumps
from uuid import uuid4
from os.path import abspath, dirname, join
from ujson import loads

import requests
from requests.exceptions import ConnectionError
from derpconf.config import verify_config
from optparse import OptionParser

from holmes.config import Config
from holmes.reviewer import Reviewer, InvalidReviewError


class HolmesWorker(object):

    def __init__(self, arguments=[]):
        self.root_path = abspath(join(dirname(__file__), '..'))

        self.uuid = uuid4().hex

        self.working = True
        self.config = None

        self._parse_opt(arguments)
        self._load_config(self.options.verbose == 3)
        self._config_logging()

        self.validators = self._load_validators()

    def run(self):
        try:
            while self.working:
                self._do_work()
                logging.debug('Nap time (%ss)' % self.config.WORKER_SLEEP_TIME)
                time.sleep(self.config.WORKER_SLEEP_TIME)
        except KeyboardInterrupt:
            logging.info('Bye.')
            self.working = False

    def stop_work(self):
        self.working = False

    def _do_work(self):
        if self._ping_api():
            err = None
            job = self._load_next_job()
            if job:
                self._start_job(job['review'])

                try:
                    self._start_reviewer(job=job)
                except InvalidReviewError:
                    err = str(sys.exc_info()[1])
                    logging.error("Fail to review %s: %s" % (job['url'], err))

                self._complete_job(job['review'], error=err)

    def _start_reviewer(self, job):
        if job:
            logging.debug('Starting Review for [%s]' % job['url'])
            reviewer = Reviewer(
                api_url=self.config.HOLMES_API_URL,
                page_uuid=job['page'],
                page_url=job['url'],
                review_uuid=job['review'],
                config=self.config,
                validators=self.validators
                )

            reviewer.review()

    def _load_validators(self, validators=None, validators_to_load=None):
        if validators_to_load is None:
            validators_to_load = self.config.VALIDATORS

        if validators is None:
            validators = []

        for validator_full_name in validators_to_load:
            if isinstance(validator_full_name, (tuple, set, list)):
                self._load_validators(validators, validator_full_name)
                continue

            try:
                module_name, class_name = validator_full_name.rsplit('.', 1)
                module = __import__(module_name, globals(), locals(), class_name)
                validators.append(getattr(module, class_name))
            except ValueError:
                logging.warn('Invalid validator name [%s]. Will be ignored.' % validator_full_name)
            except AttributeError:
                logging.warn('Validator [%s] not found. Will be ignored.' % validator_full_name)
            except ImportError:
                logging.warn('Module [%s] not found. Will be ignored.' % validator_full_name)

        return validators

    def _ping_api(self):
        try:
            requests.post('%s/worker/%s/ping' % (self.config.HOLMES_API_URL, self.uuid), data={'worker_uuid': self.uuid})
            return True
        except ConnectionError:
            logging.fatal('Fail to ping API [%s]. Stopping Worker.' % self.config.HOLMES_API_URL)
            self.working = False
            return False

    def _load_next_job(self):
        try:
            response = requests.post('%s/next' % self.config.HOLMES_API_URL, data={})
            if response and response.text:
                return loads(response.text)
        except ConnectionError:
            logging.fatal('Fail to get next review from [%s]. Stopping Worker.' % self.config.HOLMES_API_URL)
            self.working = False

    def _start_job(self, review_uuid):
        if not review_uuid:
            return False

        try:
            response = requests.post('%s/worker/%s/review/%s/start' %
                                    (self.config.HOLMES_API_URL, self.uuid, review_uuid))
            return ('OK' == response.text)

        except ConnectionError:
            logging.error('Fail to start review.')

    def _complete_job(self, review_uuid, error=None):
        if not review_uuid:
            return False

        try:
            response = requests.post('%s/worker/%s/review/%s/complete' %
                                    (self.config.HOLMES_API_URL, self.uuid, review_uuid),
                                     data=dumps({'error': error}))
            return ('OK' == response.text)
        except ConnectionError:
            logging.error('Fail to complete worker.')

    def _parse_opt(self, arguments):
        parser = OptionParser()
        parser.add_option('-c', '--conf', dest='conf', default=join(self.root_path, 'holmes/config/local.conf'),
                          help='Configuration file to use for the server.')
        parser.add_option('--verbose', '-v', action='count', default=0,
                          help='Log level: v=warning, vv=info, vvv=debug.')

        self.options, self.arguments = parser.parse_args(arguments)

    def _load_config(self, verify=False):
        if verify:
            verify_config(self.options.conf)
        self.config = Config.load(self.options.conf)

    def _config_logging(self):
        LOGS = {
            0: 'error',
            1: 'warning',
            2: 'info',
            3: 'debug'
        }

        if self.options.verbose:
            log_level = LOGS[self.options.verbose].upper()
        else:
            log_level = self.config.LOG_LEVEL.upper()

        logging.basicConfig(
            level=log_level,
            format=self.config.LOG_FORMAT,
            datefmt=self.config.LOG_DATE_FORMAT
        )

        return log_level


def main():
    worker = HolmesWorker(sys.argv[1:])
    worker.run()

if __name__ == '__main__':
    main()
