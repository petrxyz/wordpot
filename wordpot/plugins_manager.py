#!/usr/bin/env python

from flask import request
from wordpot.logger import *
import os
import configparser # ConfigParser has been renamed configparser

CURRENTPATH = os.path.abspath(os.path.dirname(__file__))

class PluginsManager():
    def __init__(self):
        self.plugins_path = os.path.join(CURRENTPATH, 'plugins/') 

        self.plugins_loaded             = {}
        self.plugins_loaded['plugins']  = []
        self.plugins_loaded['themes']   = []
        self.plugins_loaded['admin']    = []
        self.plugins_loaded['commons']  = []
        return

    def _import_plugin(self, name):
        mod = __import__(name)
        components = name.split('.')
        for c in components[1:]:
            mod = getattr(mod, c)
        return (mod)

    def load(self):
        for root, dirs, files in os.walk(self.plugins_path):
            for file in files:
                if file[-3:] == '.py' and file != '__init__.py':
                    modname = 'wordpot.plugins.' + file[:-3]
                    plugin = self._import_plugin(modname).Plugin() 
                    plugin._load_config(file[:-3])

                    # Add to loaded list organized by categories
                    for h in plugin.hooks: 
                        self.plugins_loaded[h].append(plugin)

    def hook(self, hook):
        return (self.plugins_loaded[hook])
                    
class BasePlugin(object):
    def __init__(self, slug=None):
        self.name           = None
        self.author         = None
        self.link           = None  
        self.description    = None
        self.version        = None
        
        self.slug           = None
        self.hooks          = None
        
        self.request        = None

        self.inputs         = {}
        self.outputs        = {}

    def _load_config(self, slug=None):
        self.slug = slug
        try:
            config = configparser.ConfigParser()
            plugin_config = os.path.join(CURRENTPATH, 'plugins/%s.ini' % self.slug)

            config.read(plugin_config)

            self.name = config.get('plugin', 'name')
            self.author = config.get('plugin', 'author')
            self.link = config.get('plugin', 'link')
            self.description = config.get('plugin', 'description')
            self.version = config.get('plugin', 'version')

            self.hooks = [v.strip() for v in config.get('plugin', 'hooks').split(',')]
        except Exception as e:
            pass
    
    def start(self, **kwargs):
        # First flush previous inputs/outputs
        self.inputs = {}
        self.outputs = {}

        # Parse arguments 
        for k, v in kwargs.items():
            self.inputs[k] = v
        try:
            self.run()
        except Exception as e:
            LOGGER.error('Unable to run plugin: %s\n%s', self.name, e.message)

    def run(self):
        return

    def to_json_log(self, **kwargs):
        from datetime import datetime
        import json
        from user_agents import parse

        # Parse the User-Agent string
        user_agent_string = self.inputs['request'].user_agent.string
        user_agent = parse(user_agent_string)

        # Get current time in ISO 8601 format
        timestamp = datetime.now().isoformat()

        # Flatten user agent details into top-level fields
        log_data = {
            "timestamp": timestamp,
            "src_ip": self.inputs['request'].remote_addr,
            "src_port": self.inputs['request'].environ['REMOTE_PORT'],
            "dest_ip": self.inputs['request'].environ['SERVER_NAME'],
            "dest_port": self.inputs['request'].environ['SERVER_PORT'],
            "browser_family": user_agent.browser.family,
            "browser_version": user_agent.browser.version_string,
            "os_family": user_agent.os.family,
            "os_version": user_agent.os.version_string,
            "device_family": user_agent.device.family,
            "user_agent": user_agent_string,
            "url": self.inputs['request'].url,
            **kwargs
        }

        return json.dumps(log_data)
