# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import codecs
import logging
import re

from datetime import datetime
from difflib import unified_diff

from bumpr.helpers import execute, BumprError
from bumpr.hooks import HOOKS
from bumpr.vcs import VCS
from bumpr.version import Version

logger = logging.getLogger(__name__)


class Releaser(object):
    '''
    Release workflow executor
    '''
    def __init__(self, config):
        self.config = config

        with open(config.file) as f:
            match = re.search(config.regex, f.read())
            try:
                version_string = match.group('version')
                self.prev_version = Version.parse(version_string)
            except:
                raise BumprError('Version not found in {}'.format(config.file))

        logger.debug('Previous version: {0}'.format(self.prev_version))

        self.version = self.prev_version.copy()
        self.version.bump(config.bump.part, config.bump.unsuffix, config.bump.suffix)
        logger.debug('Bumped version: {0}'.format(self.version))

        self.next_version = self.version.copy()
        self.next_version.bump(config.prepare.part, config.prepare.unsuffix, config.prepare.suffix)
        logger.debug('Prepared version: {0}'.format(self.next_version))

        self.timestamp = None

        if config.vcs:
            self.vcs = VCS[config.vcs](verbose=config.verbose)
            self.vcs.validate()

        if config.dryrun:
            self.diffs = {}

        self.hooks = [hook(self) for hook in HOOKS if self.config[hook.key]]

    def execute(self, command, version=None, verbose=None):
        version = version or self.version
        verbose = verbose or self.config.verbose
        replacements = dict(version=version, date=self.timestamp, **version.__dict__)
        execute(command, replacements=replacements, dryrun=self.config.dryrun, verbose=verbose)

    def release(self):
        self.timestamp = datetime.now()

        if self.config.bump_only:
            self.bump()
        elif self.config.prepare_only:
            self.prepare()
        else:
            self.clean()
            self.test()
            self.bump()
            self.publish()
            self.prepare()

    def test(self):
        if self.config.tests:
            logger.info('Running test suite')
            self.execute(self.config.tests, verbose=True)

    def bump(self):
        logger.info('Bump version %s', self.version)

        replacements = [
            (str(self.prev_version), str(self.version))
        ]

        for hook in self.hooks:
            hook.bump(replacements)

        self.bump_files(replacements)

        if self.config.vcs:
            self.commit(self.config.bump.message.format(
                version=self.version,
                date=self.timestamp,
                **self.version.__dict__
            ))
            self.tag()

        if self.config.dryrun:
            self.display_diff()
            self.diffs.clear()

    def prepare(self):
        logger.info('Prepare version %s', self.next_version)

        replacements = [
            (str(self.version), str(self.next_version))
        ]

        for hook in self.hooks:
            hook.prepare(replacements)

        self.bump_files(replacements)

        if self.config.vcs:
            self.commit(self.config.prepare.message.format(
                version=self.next_version,
                date=self.timestamp,
                **self.next_version.__dict__
            ))

        if self.config.dryrun:
            self.display_diff()

    def clean(self):
        '''Clean the workspace'''
        if self.config.clean:
            logger.info('Cleaning')
            self.execute(self.config.clean)

    def perform(self, filename, before, after):
        if self.config.dryrun:
            diff = unified_diff(before.split('\n'), after.split('\n'), lineterm='')
            self.diffs[filename] = diff
        else:
            with open(filename, 'wb') as f:
                f.write(after.encode(self.config.encoding))

    def bump_files(self, replacements):
        for filename in [self.config.file] + self.config.files:
            with codecs.open(filename, 'r', self.config.encoding) as current_file:
                before = current_file.read()
            after = before
            for token, replacement in replacements:
                after = after.replace(token, replacement)
            self.perform(filename, before, after)

    def publish(self):
        '''Publish the current release to PyPI'''
        if self.config.publish:
            logger.info('Publish')
            self.execute(self.config.publish)

    def tag(self):
        if self.config.tag:
            logger.debug('Tag: %s', self.version)
            if not self.config.dryrun:
                self.vcs.tag(str(self.version))
            else:
                logger.dryrun('tag: {0}'.format(self.version))

    def commit(self, message):
        if self.config.commit:
            logger.debug('Commit: %s', message)
            if not self.config.dryrun:
                self.vcs.commit(message)
            else:
                logger.dryrun('commit: {0}'.format(message))

    def display_diff(self):
        for filename, diff in self.diffs.items():
            logger.diff(filename)
            for line in diff:
                logger.diff(line)
            logger.diff('')
