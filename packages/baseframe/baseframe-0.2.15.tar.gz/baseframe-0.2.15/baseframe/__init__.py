# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os
from datetime import datetime, timedelta
import requests
from flask import Blueprint, send_from_directory, render_template, current_app
from coaster.assets import split_namespec
from flask.ext.assets import Environment, Bundle
from ._version import *
from .assets import assets, Version

__all__ = ['baseframe', 'baseframe_js', 'baseframe_css', 'assets', 'Version']


class BaseframeBlueprint(Blueprint):
    def init_app(self, app, requires=[], bundle_js=None, bundle_css=None, assetenv=None):
        """
        Initialize an app and load necessary assets.

        :param requires: List of required assets. If an asset has both .js
        and .css components, both will be added to the requirement list.
        Loaded assets will be minified and concatenated into the app's
        ``static/js`` and ``static/css`` folders. If an asset has problems
        with either of these, it should be loaded pre-bundled via the
        ``bundle_js`` and ``bundle_css`` parameters.
        :param bundle_js: Bundle of additional JavaScript.
        :param bundle_css: Bundle of additional CSS.
        """
        assets_js = []
        assets_css = []
        for item in requires:
            name, spec = split_namespec(item)
            for alist, ext in [(assets_js, '.js'), (assets_css, '.css')]:
                if name + ext in assets:
                    alist.append(name + ext + unicode(spec))
        js_all = Bundle(assets.require('!jquery.js', *assets_js),
            filters='closure_js', output='js/baseframe-packed.js')
        css_all = Bundle(assets.require(*assets_css),
            filters=['cssrewrite', 'cssmin'], output='css/baseframe-packed.css')
        if bundle_js:
            js_all = Bundle(js_all, bundle_js)
        if bundle_css:
            css_all = Bundle(css_all, bundle_css)

        if assetenv is None:
            app.assets = Environment(app)
        else:
            app.assets = assetenv
        app.assets.register('js_jquery', assets.require('jquery.js'))
        app.assets.register('js_all', js_all)
        app.assets.register('css_all', css_all)
        app.register_blueprint(self)

        if 'NETWORKBAR_DATA' not in app.config:
            app.config['NETWORKBAR_DATA'] = 'https://api.hasgeek.com/1/networkbar/networkbar.json'

        self.load_networkbar_data(app)

    def load_networkbar_data(self, app):
        if not app.config.get('NETWORKBAR_LINKS'):
            if isinstance(app.config['NETWORKBAR_DATA'], basestring):
                try:
                    r = requests.get(app.config['NETWORKBAR_DATA'])
                    app.config['NETWORKBAR_LINKS'] = (
                        r.json() if callable(r.json) else r.json).get('links', [])
                except:  # Catch all exceptions
                    app.config['NETWORKBAR_LINKS'] = []
            elif isinstance(app.config['NETWORKBAR_DATA'], (list, tuple)):
                app.config['NETWORKBAR_LINKS'] = app.config['NETWORKBAR_DATA']
            else:
                app.config['NETWORKBAR_LINKS'] = []


baseframe = BaseframeBlueprint('baseframe', __name__,
    static_folder='static',
    static_url_path='/_baseframe',
    template_folder='templates')


@baseframe.route('/favicon.ico')
def favicon():
    app_icon_path = current_app.static_folder
    # Does the app have a favicon.ico in /static?
    if not os.path.exists(os.path.join(app_icon_path, 'favicon.ico')):
        # Nope? Is it in /static/img?
        app_icon_path = os.path.join(current_app.static_folder, 'img')
        if not os.path.exists(os.path.join(app_icon_path, 'favicon.ico')):
            # Still nope? Serve default favicon from baseframe
            app_icon_path = os.path.join(baseframe.static_folder, 'img')
    return send_from_directory(app_icon_path,
      'favicon.ico', mimetype='image/vnd.microsoft.icon')


@baseframe.route('/humans.txt')
def humans():
    return send_from_directory(
        current_app.static_folder if os.path.exists(
            os.path.join(current_app.static_folder, 'humans.txt')) else baseframe.static_folder,
        'humans.txt', mimetype='text/plain')


@baseframe.route('/robots.txt')
def robots():
    return send_from_directory(
        current_app.static_folder if os.path.exists(
            os.path.join(current_app.static_folder, 'robots.txt')) else baseframe.static_folder,
        'robots.txt', mimetype='text/plain')


@baseframe.route('/_toastr_messages.js')
def toastr_messages_js():
    return current_app.response_class(render_template('toastr_messages.js'), mimetype='application/javascript')


@baseframe.route('/_editor.css')
def editorcss():
    response = current_app.response_class(render_template('editor.css'),
        mimetype='text/css',
        headers={'Expires': (datetime.utcnow() + timedelta(minutes=60)).strftime('%a, %d %b %Y %H:%M:%S GMT')})
    return response


@baseframe.app_errorhandler(404)
def error404(e):
    return render_template('404.html'), 404


@baseframe.app_errorhandler(403)
def error403(e):
    return render_template('403.html'), 403


@baseframe.app_errorhandler(500)
def error500(e):
    return render_template('500.html'), 500


@baseframe.app_template_filter('age')
def age(dt):
    suffix = u"ago"
    delta = datetime.utcnow() - dt
    if delta.days == 0:
        # < 1 day
        if delta.seconds < 10:
            return "seconds %s" % suffix
        elif delta.seconds < 60:
            return "%d seconds %s" % (delta.seconds, suffix)
        elif delta.seconds < 120:
            return "a minute %s" % suffix
        elif delta.seconds < 3600:  # < 1 hour
            return "%d minutes %s" % (int(delta.seconds / 60), suffix)
        elif delta.seconds < 7200:  # < 2 hours
            return "an hour %s" % suffix
        else:
            return "%d hours %s" % (int(delta.seconds / 3600), suffix)
    elif delta.days == 1:
        return u"a day %s" % suffix
    else:
        return u"%d days %s" % (delta.days, suffix)


@baseframe.after_app_request
def process_response(response):
    # Prevent pages from being placed in an iframe. If the response already
    # set has a value for this option, let it pass through
    if 'X-Frame-Options' in response.headers:
        frameoptions = response.headers.get('X-Frame-Options')
        # FIXME: There has to be a better way to signal this.
        if not frameoptions or frameoptions == 'ALLOW':
            response.headers.pop('X-Frame-Options')
    else:
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response


# Deprecated imports
from .deprecated import *
