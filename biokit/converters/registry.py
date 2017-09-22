import sys
import os
import inspect
import itertools
import pkgutil
import importlib

import biokit.converters


class Registry(object):

    def __init__(self):
        self._registry = {}
        self._fill_registry(biokit.converters.__path__)


    def _fill_registry(self, path):
        """
        Explore the directory converters to discover all converter classes
        (a concrete class which inherits from :class:`ConvBase`)
        and fill the register with the all input extensions, output extensions associated to this converter

        :param str path: the path of a directory to explore (not recursive)
        """

        def is_converter(item):
            obj_name, obj = item
            if not inspect.isclass(obj):
                return False
            return issubclass(obj, biokit.converters.base.ConvBase) and not inspect.isabstract(obj)

        modules = pkgutil.iter_modules(path=path)
        for _ ,module_name , *_ in modules :
            if module_name not in ('__init__', 'base', 'registry'):
                try:
                    module = importlib.import_module("biokit.converters." + module_name)
                except (ImportError, TypeError) as err:
                    print(">>> WARNING skip module '{}': {} <<<".format(module_name, err, file=sys.stderr))
                    continue
                converters = inspect.getmembers(module)
                converters = [c for c in converters if is_converter(c)]
                for converter_name, converter in converters:
                    if converter is not None:
                        all_conv_path = itertools.product(converter.input_ext, converter.output_ext)
                        for conv_path in all_conv_path:
                            self[conv_path] = converter


    def __setitem__(self, conv_path, value):
        """
        Set new
        :param conv_path: the input extension, the output extension
        :type conv_path: tuple of 2 strings
        :param value: the convertor which handle the conversion from input_ext -> output_ext
        :type value: :class:`ConvBase` object
        """
        if conv_path in self._registry:
            raise KeyError('an other converter already exist for {} -> {}'.format(*conv_path))
        self._registry[conv_path] = value


    def __getitem__(self, conv_path):
        """

        :param conv_path: the input extension, the output extension
        :type conv_path: tuple of 2 strings
        :return: an object of subclass o :class:`ConvBase`
        """
        return self._registry[conv_path]


    def __contains__(self, conv_path):
        """
        can use membership operation on registry

        :param conv_path: the input extension, the output extension
        :type conv_path: tuple of 2 strings
        :return: True if conv_path is in registry otherwise False.
        """
        return conv_path in self._registry


    def __iter__(self):
        """
        make registry iterable through conv_path (str input extension, str output extension)
        """
        for path in self._registry:
            yield path

