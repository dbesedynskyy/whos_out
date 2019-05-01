import json
import os

class ConfigHelper():
    def __init__(self, configFile = 'config.json'):
        config_fname = os.path.join(os.path.dirname(__file__), configFile)
        with open(config_fname) as json_config:
            self._config = json.load(json_config)

    def _tryGetConfigParameter(self, name, default):
        if name in self._config:
            print("Reading configuration parameter: '{0}' from file".format(name))
            return self._config[name]
        print("Configuration parameter: {0} resolved in default value {1}".format(name, default))
        return default
    
    def _tryGetEnvironmentParameter(self, name, default):
        if name in os.environ:
            return os.environ[name]
        else:
            return self._tryGetConfigParameter("{0}_TEST".format(name), default)

    def getTeams(self):
        return self._tryGetConfigParameter("teams", [])

    def getDays(self):
        return self._tryGetConfigParameter("days", 7)

    def getBambooOrg(self):
        return self._tryGetEnvironmentParameter("BAMBOO_ORG", None)

    def getBambooKey(self):
        return self._tryGetEnvironmentParameter("BAMBOO_TOKEN", None)
        
    def getSlackHook(self):
        return self._tryGetEnvironmentParameter("SLACK_HOOK", None)