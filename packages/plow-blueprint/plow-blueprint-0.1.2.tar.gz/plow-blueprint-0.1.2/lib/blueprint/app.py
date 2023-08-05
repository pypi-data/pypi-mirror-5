
import os
import argparse
import logging
import yaml
import pprint 

import conf

from exception import BlueprintException

logger = logging.getLogger(__name__)

__all__ = [
    "Application",
    "PluginManager",
    "BlueprintRunner",
    "loadBackendPlugin",
    "loadScript"]


class EventManager(object):
    pass

class PluginManager(object):
    """
    The PluginManager is used to maintain a list of active plugins.
    """
    loaded = []

    @classmethod
    def loadPlugin(cls, module):
        if module in cls.loaded:
            return
        plugin = __import__(module, globals(), locals(), [module])
        try:
            plugin.init()
        except  AttributeError, e:
            pass
        logger.debug("Initialized plugin %s" % plugin)
        cls.loaded.append(plugin)

    @classmethod
    def runPreLaunch(cls, spec, job):
        logger.debug("Running pre-launch plugins on spec: %s" % spec)
        for plugin in cls.loaded:
            if getattr(plugin, "preLaunch", False):
                plugin.preLaunch(spec, job)

    @classmethod
    def runAfterInit(cls, layer):
        logger.debug("Running after init plugins on %s" % layer)
        for plugin in cls.loaded:
            if getattr(plugin, "afterInit", False):
                plugin.afterInit(layer)

    @classmethod
    def runSetup(cls, layer):
        logger.debug("Running setup plugins on %s" % layer)
        for plugin in cls.loaded:
            if getattr(plugin, "setup", False):
                plugin.setup(layer)

    @classmethod
    def runBeforeExecute(cls, layer):
        logger.debug("Running before execute plugins on %s" % layer)
        for plugin in cls.loaded:
            if getattr(plugin, "beforeExecute", False):
                plugin.beforeExecute(layer)

    @classmethod
    def runAfterExecute(cls, layer):
        logger.debug("Running after execute plugins on %s" % layer)
        for plugin in cls.loaded:
            if getattr(plugin, "afterExecute", False):
                plugin.afterExecute(layer)

    @classmethod
    def getActivePlugins(cls):
        result = []
        for plugin in conf.get("plugins"):
            if not plugin["enabled"]:
                continue
            result.append(plugin["module"])
        return result

    @classmethod
    def getLoadedPlugins(cls):
        return cls.loaded

    @classmethod
    def loadAllPlugins(cls):
        logger.debug("Loading all plugins")
        for plugin in cls.getActivePlugins():
            cls.loadPlugin(plugin)

class Application(object):
    def __init__(self, descr):

        self._runner = BlueprintRunner()

        self._argparser = argparse.ArgumentParser(description=descr)
        group = self._argparser.add_argument_group("Logging Options")
        group.add_argument("-verbose", action="store_true",
            help="Turn on verbose logging.")
        group.add_argument("-debug", action="store_true",
            help="Turn on debug logging.")
        group.add_argument("-host", metavar="HOSTNAME",
            help="Specify the server to communicate with, if any.")
        group.add_argument("-backend", metavar="BACKEND",
            help="Specify the queuing backend plugin.")

    def handleArgs(self, args):
        pass

    def go(self):
        args = self._argparser.parse_args()

        # Handle the common arguments.
        if args.verbose:
            logging.basicConfig(level=logging.INFO)
        if args.debug:
            logging.basicConfig(level=logging.DEBUG)
        
        if args.host:
            self._runner.setArg("host", args.host)
        if args.backend:
            self._runner.setArg("backend", args.backend)

        # Handle arguments added by specific application.
        self.handleArgs(args)


# A simple object to use as a BlueprintRunner.getArg() default
# value rather than None, which could be a valid value.
LoadDefault = object()

class BlueprintRunner(object):

    def __init__(self, **kwargs):
        self.__args = {}
        self.__defaults = {
            "host": None, 
            "pause": False,
            "backend": conf.get("bp.backend", default="plow"),
            "name": "",
            "pretend": False,
            "script": None,
            "frame_range": None,
            "env": { }
        }
        self.__args.update(kwargs)
        self.__job = None

    def setArg(self, key, value):
        self.__args[key] = value

    def getArg(self, key, default=LoadDefault):
        try:
            return self.__args[key]
        except KeyError:
            if default is LoadDefault:
                return self.__defaults.get(key)
            return default

    def launch(self):

        logger.debug("Blueprint runner args:")
        logger.debug(self.__args)

        backend_module = self.getArg("backend")
        if not backend_module:
            raise BlueprintException("No backend module is set, see defaults.backend setting in config.")
        
        logging.debug("Launching job with backend: %s" % backend_module)
        backend = loadBackendPlugin(backend_module)

        self.setup()
        spec = backend.serialize(self)
        PluginManager.runPreLaunch(spec, self.__job)
        
        if self.getArg("pretend"):
            pprint.pprint(spec)
        else:
            backend.launch(self, spec)

    def setup(self):
        return self.getJob().setup()

    def getJob(self):
        if not self.__job:
            self.__job = loadScript(self.getArg("script"))
            if self.getArg("name", None):
                self.__job.setName(self.getArg("name"))
        return self.__job


def loadBackendPlugin(name):
    logger.debug("loading queue backend: %s" % name)
    return __import__("blueprint.backend.%s" % name, globals(), locals(), [name])

def loadScript(path):

    from blueprint.job import Job
    if os.path.basename(path) == "blueprint.yaml":
        Job.Current = yaml.load(file(path, 'r'))
        # Yamlized jobs have no session but they
        # have a path that points to one so we have
        # to bring back the archive.
        if Job.Current.getPath():
            Job.Current.loadArchive()
    else:
        Job.Current = Job(os.path.basename(path.split(".")[0]))
        execfile(path, {})

    return Job.Current






