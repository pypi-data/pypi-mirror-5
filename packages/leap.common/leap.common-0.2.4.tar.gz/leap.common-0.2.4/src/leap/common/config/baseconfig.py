# -*- coding: utf-8 -*-
# baseconfig.py
# Copyright (C) 2013 LEAP
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Implements the abstract base class for configuration
"""

import copy
import logging
import functools
import os

from abc import ABCMeta, abstractmethod

from leap.common.check import leap_assert
from leap.common.files import mkdir_p
from leap.common.config.pluggableconfig import PluggableConfig
from leap.common.config.prefixers import get_platform_prefixer

logger = logging.getLogger(__name__)


class BaseConfig:
    """
    Abstract base class for any JSON based configuration
    """

    __metaclass__ = ABCMeta

    """
    Standalone is a class wide parameter

    @param standalone: if True it will return the prefix for a
    standalone application. Otherwise, it will return the system
    default for configuration storage.
    @type standalone: bool
    """
    standalone = False

    def __init__(self):
        self._data = {}
        self._config_checker = None

    @abstractmethod
    def _get_spec(self):
        """
        Returns the spec object for the specific configuration
        """
        return None

    def _safe_get_value(self, key):
        """
        Tries to return a value only if the config has already been loaded

        @rtype: depends on the config structure, dict, str, array, int
        @return: returns the value for the specified key in the config
        """
        leap_assert(self._config_checker, "Load the config first")
        return self._config_checker.config.get(key, None)

    def get_path_prefix(self):
        """
        Returns the platform dependant path prefixer
        """
        return get_platform_prefixer().get_path_prefix(
            standalone=self.standalone)

    def loaded(self):
        """
        Returns True if the configuration has been already
        loaded. False otherwise
        """
        return self._config_checker is not None

    def save(self, path_list):
        """
        Saves the current configuration to disk

        @param path_list: list of components that form the relative
        path to configuration. The absolute path will be calculated
        depending on the platform.
        @type path_list: list

        @return: True if saved to disk correctly, False otherwise
        """
        config_path = os.path.join(self.get_path_prefix(), *(path_list[:-1]))
        mkdir_p(config_path)

        try:
            self._config_checker.serialize(os.path.join(config_path,
                                                        path_list[-1]))
        except Exception as e:
            logger.warning("%s" % (e,))
            raise
        return True

    def load(self, path="", data=None, mtime=None):
        """
        Loads the configuration from disk

        @type path: str
        @param path: relative path to configuration. The absolute path
        will be calculated depending on the platform

        @return: True if loaded from disk correctly, False otherwise
        """

        config_path = os.path.join(self.get_path_prefix(),
                                   path)

        self._config_checker = PluggableConfig(format="json")
        self._config_checker.options = copy.deepcopy(self._get_spec())

        try:
            if data is None:
                self._config_checker.load(fromfile=config_path, mtime=mtime)
            else:
                self._config_checker.load(data, mtime=mtime)
        except Exception as e:
            logger.warning("Something went wrong while loading " +
                           "the config from %s\n%s" % (config_path, e))
            self._config_checker = None
            return False
        return True


class LocalizedKey(object):
    """
    Decorator used for keys that are localized in a configuration
    """

    def __init__(self, func, **kwargs):
        self._func = func

    def __call__(self, instance, lang="en"):
        """
        Tries to return the string for the specified language, otherwise
        informs the problem and returns an empty string

        @param lang: language code
        @type lang: str

        @return: localized value from the possible values returned by
        self._func
        """
        descriptions = self._func(instance)
        description_lang = ""
        config_lang = "en"
        for key in descriptions.keys():
            if lang.startswith(key):
                config_lang = key
                break

        description_lang = descriptions[config_lang]
        return description_lang

    def __get__(self, instance, instancetype):
        """
        Implement the descriptor protocol to make decorating instance
        method possible.
        """
        # Return a partial function with the first argument is the instance
        # of the class decorated.
        return functools.partial(self.__call__, instance)

if __name__ == "__main__":
    try:
        config = BaseConfig()  # should throw TypeError for _get_spec
    except Exception as e:
        assert isinstance(e, TypeError), "Something went wrong"
        print "Abstract BaseConfig class is working as expected"
