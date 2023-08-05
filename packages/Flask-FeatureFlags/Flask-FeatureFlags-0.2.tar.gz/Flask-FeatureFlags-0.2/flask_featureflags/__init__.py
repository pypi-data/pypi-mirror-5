"""
(c) 2013 Rachel Sanders.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
   limitations under the License.
"""

from functools import wraps
import logging

from flask import abort, current_app, g, redirect

__version__ = u'0.1'

log = logging.getLogger(u'flask-featureflags')

class StopCheckingFeatureFlags(Exception):
  """ Raise this inside of a feature flag handler to immediately return False and stop any further handers from running """
  pass

def AppConfigFlagHandler(feature=None):
  """ This is the default handler. It checks for feature flags in the current app's configuration.

  For example, to have 'unfinished_feature' hidden in production but active in development:

  config.py

  class ProductionConfig(Config):

    FEATURE_FLAGS = {
      'unfinished_feature' : False,
    }


  class DevelopmentConfig(Config):

    FEATURE_FLAGS = {
      'unfinished_feature' : True,
    }

   """
  if current_app is None:
    log.warn(u"Got a request to check for %s but we're outside the request context. Returning False" % feature)
    return False

  try:
    return current_app.config[u'FEATURE_FLAGS'][feature]
  except (AttributeError, KeyError):
    log.info(u"No feature flag defined for %s" % feature)
    return False

class FeatureFlag(object):

  def __init__(self, app):
    if app is not None:
      self.init_app(app)

    # The default out-of-the-box handler looks up features in Flask's app config.
    self.handlers = [AppConfigFlagHandler]

  def init_app(self, app):
    """ Inject ourself into the request setup and add a jinja function test """
    app.before_request(self.process_request)
    app.jinja_env.tests[u'active_feature'] = self.check

  def process_request(self):
    """ Load ourselves into the globals """
    g.feature_flags = self

  def clear_handlers(self):
    """ Clear all handlers. This effectively turns every feature off."""
    self.handlers = []

  def add_handler(self, function):
    """ Add a new handler to the end of the chain of handlers. """
    self.handlers.append(function)

  def remove_handler(self, function):
    """ Remove a handler from the chain of handlers.  """
    try:
      self.handlers.remove(function)
    except ValueError: # handler wasn't in the list, pretend we don't notice
      pass

  def check(self, feature):
    """ Loop through all our feature flag checkers and return true if any of them are true.

    The order of handlers matters - we will immediately return True if any handler returns true.

    If you want to a handler to return False and stop the chain, raise the StopCheckingFeatureFlags exception."""
    for handler in self.handlers:
      try:
        if handler(feature): return True
      except StopCheckingFeatureFlags:
        return False
    else:
      return False


def is_active(feature):
  """ Check if a feature is active """
  if hasattr(g, u'feature_flags') and isinstance(g.feature_flags, FeatureFlag):
    return g.feature_flags.check(feature)
  else:
    log.warn(u'Got a request to check for %s but no handlers are configured. Check your setup. Returning False' % feature)
    return False

def is_active_feature(feature, redirect_to=None):
  """
  Decorator for Flask views. If a feature is off, it can either return a 404 or redirect to a URL if you'd rather.
  """
  def _is_active_feature(func):
    @wraps(func)
    def wrapped(*args, **kwargs):

      if not is_active(feature):
        if redirect_to:
          log.debug(u'Feature %s is off, redirecting to %s' % (feature, redirect_to))
          return redirect(redirect_to, code=302)
        else:
          log.debug(u'Feature %s is off, aborting request' % feature)
          abort(404)

      return func(*args, **kwargs)
    return wrapped
  return _is_active_feature