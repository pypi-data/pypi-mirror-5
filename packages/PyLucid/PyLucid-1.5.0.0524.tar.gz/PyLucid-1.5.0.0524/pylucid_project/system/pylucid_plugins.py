# coding: utf-8

"""
    PyLucid plugins
    ~~~~~~~~~~~~~~~

    :copyleft: 2009-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.p

"""


import logging
import os
import pprint
import sys

from django.conf import settings
from django.conf.urls.defaults import patterns, include
from django.core import urlresolvers
from django.http import HttpResponse
from django.utils.importlib import import_module
from django.utils.log import getLogger
from django.views.decorators.csrf import csrf_protect

from pylucid_project.utils.python_tools import has_init_file


logger = getLogger("pylucid.pylucid_plugins")
#logger.setLevel(logging.DEBUG)
#logger.addHandler(logging.StreamHandler())


#PYLUCID_PLUGINS = None

_PLUGIN_OBJ_CACHE = {} # cache for PyLucidPlugin.get_plugin_object()
_PLUGIN_URL_CACHE = {} # cache for PyLucidPlugin.get_prefix_urlpatterns()


class PluginNotOnSite(Exception):
    """ PluginPage doesn't exist on current page. """
    pass


class PyLucidPlugin(object):
    """ represents one PyLucid plugins """

    class ObjectNotFound(Exception):
        """ Can't import a plugin module or a module Attribute doesn't exist. """
        pass

    def __init__(self, pkg_path, section, pkg_dir, plugin_name):
        # e.g.: "PYLUCID_BASE_PATH/pylucid_project/pylucid_plugins", "pylucid_project", "pylucid_plugins", "PluginName"
        self.name = plugin_name

        self.fs_path = os.path.join(pkg_path, plugin_name)
        assert os.path.isdir(self.fs_path), "path %r is not a directory or doesn't exist." % self.fs_path
        assert has_init_file(self.fs_path), "%r contains no __init__.py file!" % self.fs_path

        self.pkg_string = ".".join([pkg_dir, plugin_name])
        self.installed_apps_string = ".".join([section, self.pkg_string])

        template_dir = os.path.join(self.fs_path, "templates")
        if os.path.isdir(template_dir):
            self.template_dir = template_dir
        else:
            self.template_dir = None

    def __unicode__(self):
        return u"PyLucid plugin %r (%r)" % (self.name, self.installed_apps_string)

    def __repr__(self):
        return "<%s>" % self.__unicode__()

    def get_plugin_module(self, mod_name):
        """
        Get a module from this plugin.
        argument e.g.:
            mod_name="urls"
        """
#        print "get_plugin_module(%r)" % mod_name
        mod_pkg = ".".join([self.pkg_string, mod_name])
        if mod_pkg in _PLUGIN_OBJ_CACHE:
#            print "use _PLUGIN_OBJ_CACHE[%r]" % mod_pkg
            return _PLUGIN_OBJ_CACHE[mod_pkg]

        try:
            mod = import_module(mod_pkg)
        except Exception, err:
            msg = u"Error importing %r from plugin %r" % (mod_pkg, self.name)

            if str(err).startswith("No module named "):
                raise self.ObjectNotFound("%s: %s" % (msg, err))

            # insert more information into the traceback
            etype, evalue, etb = sys.exc_info()
#            msg += " (Syspath: %s)" % (repr(sys.path))
            evalue = etype('%s: %s' % (msg, evalue))
            raise etype, evalue, etb

#        print "put in _PLUGIN_OBJ_CACHE[%r]" % mod_pkg
        _PLUGIN_OBJ_CACHE[mod_pkg] = mod
        return mod

    def get_plugin_object(self, mod_name, obj_name):
        """
        return a object from this plugin
        argument e.g.: ("admin_urls", "urlpatterns")
        """
        cache_key = ".".join([self.pkg_string, mod_name, obj_name])
        if cache_key in _PLUGIN_OBJ_CACHE:
#            print "use _PLUGIN_OBJ_CACHE[%r]" % cache_key
            return _PLUGIN_OBJ_CACHE[cache_key]

        mod = self.get_plugin_module(mod_name)

        try:
            object = getattr(mod, obj_name)
        except AttributeError, err:
            raise self.ObjectNotFound(err)

#        print "put in _PLUGIN_OBJ_CACHE[%r]" % cache_key
        _PLUGIN_OBJ_CACHE[cache_key] = object

        return object

    def get_callable(self, mod_name, func_name):
        """ returns the callable function. """
        callable = self.get_plugin_object(mod_name, obj_name=func_name)
        return callable

    def call_plugin_view(self, request, mod_name, func_name, method_kwargs):
        """
        Call a plugin view
        used for pylucid-get-views and lucidTag calls 
        """
        callable = self.get_callable(mod_name, func_name)

        # Add info for pylucid_project.apps.pylucid.context_processors.pylucid
        request.plugin_name = self.name
        request.method_name = func_name

        csrf_exempt = getattr(callable, 'csrf_exempt', False)
        if func_name == "http_get_view" and not csrf_exempt:
            # Use csrf_protect only in pylucid get views and not für lucidTag calls
            callable = csrf_protect(callable)

        # call the plugin view method
        response = callable(request, **method_kwargs)

        if csrf_exempt and isinstance(response, HttpResponse):
            response.csrf_exempt = True

        request.plugin_name = None
        request.method_name = None
#        del(request.plugin_name)
#        del(request.method_name)

        return response

    def get_urlpatterns(self, urls_filename):
        """ returns the plugin urlpatterns """
        if "." in urls_filename:
            urls_filename = os.path.splitext(urls_filename)[0]

        raw_plugin_urlpatterns = self.get_plugin_object(mod_name=urls_filename, obj_name="urlpatterns")
        return raw_plugin_urlpatterns


    def get_prefix_urlpatterns(self, url_prefix, urls_filename):
        """ include the plugin urlpatterns with the url prefix """
        url_prefix = url_prefix.rstrip("/") + "/"

        cache_key = self.pkg_string + url_prefix
        if cache_key in _PLUGIN_URL_CACHE:
            logger.debug("use _PLUGIN_URL_CACHE[%r]" % cache_key)
            return _PLUGIN_URL_CACHE[cache_key]

        raw_plugin_urlpatterns = self.get_urlpatterns(urls_filename)

        plugin_urlpatterns = patterns('',
            (url_prefix, include(raw_plugin_urlpatterns)),
        )

        logger.debug("url prefix: %r" % url_prefix)
        logger.debug("raw_plugin_urlpatterns: %r" % raw_plugin_urlpatterns)
        logger.debug("put in _PLUGIN_URL_CACHE[%r]" % cache_key)

        _PLUGIN_URL_CACHE[cache_key] = plugin_urlpatterns

        return plugin_urlpatterns


    def get_plugin_url_resolver(self, url_prefix, urls_filename="urls"):
        prefix_urlpatterns = self.get_prefix_urlpatterns(url_prefix, urls_filename)

        logger.debug("prefix_urlpatterns: %r" % prefix_urlpatterns)

        plugin_url_resolver = urlresolvers.RegexURLResolver(r'^/', prefix_urlpatterns)

        logger.debug("reverse_dict: %s" % pprint.pformat(plugin_url_resolver.reverse_dict))

        return plugin_url_resolver

    def get_merged_url_resolver(self, url_prefix, urls_filename="urls"):
        """ Merge the globale url patterns with the plugin one, so the plugin can reverse all urls """
        prefix_urlpatterns = self.get_prefix_urlpatterns(url_prefix, urls_filename)

        ROOT_URLCONF_PATTERNS = import_module(settings.ROOT_URLCONF).urlpatterns
        merged_urlpatterns = ROOT_URLCONF_PATTERNS + prefix_urlpatterns

        # Make a own url resolver
#        merged_url_resolver = urlresolvers.RegexURLResolver(r'^/', merged_urlpatterns)
        merged_url_resolver = urlresolvers.RegexURLResolver(r'^/', merged_urlpatterns)
        return merged_url_resolver




class PyLucidPlugins(dict):
    """
    Storage for all existing PyLucid plugins
    FIXME: How can we make this lazy?
    or how can we initializied after settings?
    """

    def __init__(self):
        super(PyLucidPlugins, self).__init__()
        self.__initialized = False

    def __getattr__(self, name):
        if not self.__initialized:
            self._setup()
        assert name != "ObjectNotFound", "Don't use PYLUCID_PLUGINS.ObjectNotFound, use plugin_instance.ObjectNotFound!"
        return getattr(self, name)

    def __getitem__(self, key):
        if not self.__initialized:
            self._setup()
        return dict.__getitem__(self, key)

    def items(self, *args, **kwargs):
        if not self.__initialized:
            self._setup()
        return dict.items(self, *args, **kwargs)

    def _setup(self):
#        print " *** init PyLucidPlugins():", settings.PYLUCID_PLUGIN_SETUP_INFO.keys()
        for plugin_name, data in settings.PYLUCID_PLUGIN_SETUP_INFO.iteritems():
            pkg_path, section, pkg_dir = data
            self[plugin_name] = PyLucidPlugin(pkg_path, section, pkg_dir, plugin_name)
        self.__initialized = True

    def get_admin_urls(self):
        """
        return all existing plugin.admin_urls prefixed with the plugin name.
        Used in apps/pylucid_admin/urls.py
        """
        if not self.__initialized:
            self._setup()
        urls = []
        for plugin_name, plugin_instance in self.iteritems():
            try:
                admin_urls = plugin_instance.get_plugin_object(
                    mod_name="admin_urls", obj_name="urlpatterns"
                )
            except plugin_instance.ObjectNotFound, err:
                continue

            urls += patterns('',
                (r"^%s/" % plugin_name, include(admin_urls)),
            )

        return urls

    def call_get_views(self, request):
        """ call a pylucid plugin "html get view" and return the response. """
        if not self.__initialized:
            self._setup()
        method_name = settings.PYLUCID.HTTP_GET_VIEW_NAME
        for plugin_name in request.GET.keys():
            if plugin_name not in self:
                # get parameter is not a plugin or unknown plugin
                continue

            plugin_instance = self[plugin_name]

            # Don't display pylucid comments"
            request.PYLUCID.object2comment = False

            try:
                response = plugin_instance.call_plugin_view(
                    request, mod_name="views", func_name=method_name, method_kwargs={}
                )
            except plugin_instance.ObjectNotFound, err:
                # plugin or view doesn't exist
                if settings.DEBUG:
                    raise # Give a developer the full traceback page ;)
                else:
                    # ignore the get parameter
                    continue
            except:
                # insert more information into the traceback
                etype, evalue, etb = sys.exc_info()
                evalue = etype('Error rendering plugin view "%s.%s": %s' % (plugin_name, method_name, evalue))
                raise etype, evalue, etb

            return response



PYLUCID_PLUGINS = PyLucidPlugins()






