import inflection
import inspect
import os
import sys
import yaml

from cashew.exceptions import *

class Plugin(object):
    """
    Base class for plugins. Define instance methods shared by plugins here.
    """
    aliases = []
    _settings = {}

    def is_active(self):
        return True

    def name(self):
        return inflection.titleize(self.setting('aliases')[0])

    def help(self):
        return self.setting('help')

    def initialize_settings(self, **raw_kwargs):
        self._instance_settings = {}
        for parent_class in self.__class__.imro():
            if parent_class._settings:
                self.__class__.class_update_settings(self, parent_class._settings)
            if hasattr(parent_class, 'UNSET'):
                for unset in parent_class.UNSET:
                    del self._instance_settings[unset]

        if hasattr(self.__class__, 'aliases') and self.__class__.aliases:
            alias = self.__class__.aliases[0]
            settings_from_other_classes = PluginMeta._store_other_class_settings.get(alias)
            if settings_from_other_classes:
                self.__class__.class_update_settings(self, settings_from_other_classes)

        # Apply raw_kwargs settings
        hyphen_settings = dict((k, v) for k, v in raw_kwargs.items() if k in self._instance_settings)
        underscore_settings = dict((k.replace("_", "-"), v) for k, v in raw_kwargs.items() if k.replace("_", "-") in self._instance_settings)
        self.__class__.class_update_settings(self, hyphen_settings)
        self.__class__.class_update_settings(self, underscore_settings)

    def safe_setting(self, name_hyphen, default=None):
        """
        Retrieves the setting value, but returns a default value rather than
        raising an error if the setting does not exist.
        """
        try:
            return self.setting(name_hyphen)
        except UserFeedback:
            return default

    def setting(self, name_hyphen):
        """
        Retrieves the setting value whose name is indicated by name_hyphen.

        Values starting with $ are assumed to reference environment variables,
        and the value stored in environment variables is retrieved. (It's an
        error if there's no corresponding environment variable set.)
        """
        if name_hyphen in self._instance_settings:
            value = self._instance_settings[name_hyphen][1]
        else:
            name_underscore = name_hyphen.replace("-", "_")
            if name_underscore in self._instance_settings:
                value = self._instance_settings[name_underscore][1]
            else:
                if name_underscore == name_hyphen:
                    msg = "No setting named '%s'" % name_hyphen
                else:
                    msg = "no setting named '%s' or '%s'"
                    msg = msg % (name_hyphen, name_underscore)
                raise UserFeedback(msg)

        if hasattr(value, 'startswith') and value.startswith("$"):
            env_var = value.lstrip("$")
            if os.environ.has_key(env_var):
                return os.getenv(env_var)
            else:
                msg = "'%s' is not defined in your environment" % env_var
                raise UserFeedback(msg)
        elif hasattr(value, 'startswith') and value.startswith("\$"):
            return value.replace("\$", "$")
        else:
            return value

    def setting_values(self, skip=None):
        """
        Returns dict of all setting values (removes the helpstrings)
        """
        if not skip:
            skip = []
        return dict((k, v[1]) for k, v in self._instance_settings.iteritems() if not k in skip)

    def update_settings(self, new_settings):
        self.__class__.class_update_settings(self, new_settings, False)

class PluginMeta(type):
    """
    Base meta class for anything plugin-able.
    """
    _store_other_class_settings = {} # allow plugins to define settings for other classes

    def __init__(cls, name, bases, attrs):
        assert issubclass(cls, Plugin), "%s should inherit from class Plugin" % name
        if '__metaclass__' in attrs:
            cls.plugins = {}
        elif hasattr(cls, 'aliases'):
            cls.register_plugin(cls.aliases, cls, {})

    def register_plugin(cls, alias_or_aliases, class_or_class_name, settings):
        aliases = cls.standardize_alias_or_aliases(alias_or_aliases)
        klass = cls.get_reference_to_class(class_or_class_name)

        # Ensure 'aliases' and 'help' settings are set.
        settings['aliases'] = ('aliases', aliases)
        if not settings.has_key('help'):
            docstring = klass.check_docstring()
            settings['help'] = ("Helpstring for plugin.", docstring)

        # Create the tuple which will be registered for the plugin.
        class_info = (class_or_class_name, settings)

        # Register the class_info tuple for each alias.
        for alias in aliases:
            if isinstance(class_or_class_name, type):
                modname = class_or_class_name.__module__
                alias = cls.apply_prefix(modname, alias)

            cls.plugins[alias] = class_info

        # Register any settings defined for other classes.
        if hasattr(klass, '_other_class_settings') and klass._other_class_settings:
            PluginMeta._store_other_class_settings.update(klass._other_class_settings)

    def standardize_alias_or_aliases(cls, alias_or_aliases):
        """
        Make sure we don't attempt to iterate over an alias string thinking
        it's an array.
        """
        if isinstance(alias_or_aliases, basestring):
            return [alias_or_aliases]
        else:
            return alias_or_aliases

    def get_reference_to_class(cls, class_or_class_name):
        """
        Detect if we get a class or a name, convert a name to a class.
        """
        if isinstance(class_or_class_name, type):
            return class_or_class_name

        elif isinstance(class_or_class_name, basestring):
            if ":" in class_or_class_name:
                mod_name, class_name = class_or_class_name.split(":")

                if not mod_name in sys.modules:
                    __import__(mod_name)

                mod = sys.modules[mod_name]
                return mod.__dict__[class_name]

            else:
                return cls.load_class_from_locals(class_or_class_name)

        else:
            msg = "Unexpected Type '%s'" % type(class_or_class_name)
            raise InternalCashewException(msg)

    def load_class_from_locals(cls, class_name):
        raise Exception("not implemented")

    def check_docstring(cls):
        """
        Asserts that the class has a docstring, returning it if successful.
        """
        docstring = inspect.getdoc(cls)
        if not docstring:
            breadcrumbs = " -> ".join(t.__name__ for t in inspect.getmro(cls)[:-1][::-1])
            msg = "docstring required for plugin '%s' (%s, defined in %s)"
            args = (cls.__name__, breadcrumbs, cls.__module__)
            raise InternalCashewException(msg % args)
        return docstring

    def apply_prefix(cls, modname, alias):
        return alias

    def register_plugins(cls, plugin_info):
        for k, v in plugin_info.iteritems():
            cls.register_plugin(k.split("|"), v[0], v[1])

    def register_plugins_from_dict(cls, yaml_content):
        for alias, info_dict in yaml_content.iteritems():
            if ":" in alias:
                _, alias = alias.split(":")

            if not info_dict.has_key('class'):
                import json
                msg = "invalid info dict for %s: %s" % (alias, json.dumps(info_dict))
                raise InternalCashewException(msg)

            class_name = info_dict['class']
            del info_dict['class']
            cls.register_plugin(alias.split("|"), class_name, info_dict)

    def register_plugins_from_yaml_file(cls, yaml_file):
        with open(yaml_file, 'rb') as f:
            yaml_content = yaml.safe_load(f.read())
        cls.register_plugins_from_dict(yaml_content)

    def create_instance(cls, alias, *instanceargs, **instancekwargs):
        alias = cls.adjust_alias(alias)

        if not alias in cls.plugins:
            msg = "no alias '%s' available for '%s'"
            msgargs = (alias, cls.__name__)
            raise NoPlugin(msg % msgargs)

        class_or_class_name, settings = cls.plugins[alias]
        klass = cls.get_reference_to_class(class_or_class_name)

        instance = klass(*instanceargs, **instancekwargs)
        instance.alias = alias

        if not hasattr(instance, '_instance_settings'):
            instance.initialize_settings()
        instance.update_settings(settings)

        if not instance.is_active():
            raise InactivePlugin(alias)

        return instance

    def adjust_alias(cls, alias):
        return alias

    # documented above here

    def __iter__(cls, *instanceargs):
        processed_aliases = set()
        for alias in sorted(cls.plugins):
            if alias in processed_aliases:
                continue

            try:
                instance = cls.create_instance(alias, *instanceargs)
                yield(instance)
                for alias in instance.aliases:
                    processed_aliases.add(alias)

            except InactivePlugin:
                pass

    def standardize_alias(cls, alias):
        obj = cls.plugins[alias]
        keys = []
        for k, v in cls.plugins.iteritems():
            if v == obj:
                keys.append(k)
        assert alias in keys
        return sorted(keys)[0]


    def imro(cls):
        """
        Returns MRO in reverse order, skipping 'object/type' class.
        """
        return reversed(inspect.getmro(cls)[0:-2])

    def class_update_settings(cls, instance, new_settings, enforce_helpstring=True):
        for raw_key, value in new_settings.iteritems():
            key = raw_key.replace("_", "-")
            key_in_settings = instance._instance_settings.has_key(key)
            value_is_list_len_2 = isinstance(value, list) and len(value) == 2
            if isinstance(value, tuple) or (not key_in_settings and value_is_list_len_2):
                instance._instance_settings[key] = value
            else:
                if not instance._instance_settings.has_key(key):
                    if enforce_helpstring:
                        raise Exception("You must specify param '%s' as a tuple of (helpstring, value)" % key)
                    else:
                        # TODO check and warn if key is similar to an existing key
                        instance._instance_settings[key] = ('', value,)
                else:
                    orig = instance._instance_settings[key]
                    instance._instance_settings[key] = (orig[0], value,)
