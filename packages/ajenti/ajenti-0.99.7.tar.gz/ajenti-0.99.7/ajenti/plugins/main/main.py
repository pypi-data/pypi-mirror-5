import json
import gevent
from base64 import b64encode
import zlib
import traceback

import ajenti
from ajenti.api import *
from ajenti.api.http import *
from ajenti.api.sensors import Sensor
from ajenti.middleware import AuthenticationMiddleware
from ajenti.profiler import *
from ajenti.users import PermissionProvider, UserManager, SecurityError
from ajenti.ui import *
from ajenti.util import make_report
import ajenti.feedback

from api import SectionPlugin


@plugin
class MainServer (BasePlugin, HttpPlugin):
    @url('/')
    def handle_index(self, context):
        context.add_header('Content-Type', 'text/html')
        if context.session.identity is None:
            context.respond_ok()
            return self.open_content('static/auth.html').read()
        context.respond_ok()
        return self.open_content('static/index.html').read()

    @url('/ajenti:auth')
    def handle_auth(self, context):
        username = context.query.getvalue('username', '')
        password = context.query.getvalue('password', '')
        if not AuthenticationMiddleware.get().try_login(context, username, password):
            gevent.sleep(3)
        return context.redirect('/')

    @url('/ajenti:logout')
    def handle_logout(self, context):
        AuthenticationMiddleware.get().logout(context)
        context.session.destroy()
        return context.redirect('/')


@plugin
class MainSocket (SocketPlugin):
    name = '/stream'

    def on_connect(self):
        if not 'ui' in self.request.session.data:
            # This is a newly created session
            ui = UI.new()

            self.request.session.data['ui'] = ui
            ui.root = MainPage.new(ui)
            ui.root.username = self.request.session.identity
            sections_root = SectionsRoot.new(ui)

            for e in sections_root.startup_crashes:
                self.send_crash(e)

            ui.root.append(sections_root)
            ui._sections = sections_root.children
            ui._sections_root = sections_root

        self.ui = self.request.session.data['ui']
        self.send_init()
        self.send_ui()
        self.spawn(self.ui_watcher)

        # Inject into session
        self.request.session.endpoint = self

        # Inject the context methods
        self.context.notify = self.send_notify
        self.context.launch = self.launch
        self.context.endpoint = self

    def on_message(self, message):
        try:
            if message['type'] == 'ui_update':
                # UI updates arrived
                profile('Total')
                for update in message['content']:
                    if update['type'] == 'update':
                        # Property change
                        profile('Handling updates')
                        el = self.ui.find_uid(update['uid'])
                        for k, v in update['properties'].iteritems():
                            el.properties[k].set(v)
                            el.properties[k].dirty = False
                        profile_end('Handling updates')
                    if update['type'] == 'event':
                        # Element event emitted
                        profile('Handling event')
                        self.ui.dispatch_event(update['uid'], update['event'], update['params'])
                        profile_end('Handling event')
                if self.ui.has_updates():
                    # If any updates happened due to event handlers, send these immediately
                    self.ui.clear_updates()
                    self.send_ui()
                else:
                    # Otherwise just ACK
                    self.send_ack()
                profile_end('Total')
                if ajenti.debug:
                    self.send_debug()
        except SecurityError, e:
            self.send_security_error()
        except Exception, e:
            self.send_crash(e)

    def send_init(self):
        data = {
            'version': ajenti.version,
            'platform': ajenti.platform,
            'hostname': Sensor.find('hostname').value(),
        }
        self.emit('init', json.dumps(data))

    def send_ui(self):
        profile('Rendering')
        data = json.dumps(self.ui.render())
        profile_end('Rendering')
        data = b64encode(zlib.compress(data)[2:-4])
        self.emit('ui', data)

    def send_ack(self):
        self.emit('ack')

    def send_update_request(self):
        self.emit('update-request')

    def send_security_error(self):
        self.emit('security-error', '')

    def send_url(self, url, title='new tab'):
        self.emit('url', json.dumps({'url': url, 'title': title}))

    def send_debug(self):
        data = {
            'profiles': get_profiles()
        }
        self.emit('debug', json.dumps(data))

    def send_crash(self, exc):
        if not hasattr(exc, 'traceback'):
            exc.traceback = traceback.format_exc(exc)
        data = {
            'message': str(exc),
            'traceback': exc.traceback,
            'report': make_report()
        }
        data = json.dumps(data)
        self.emit('crash', data)

    def send_notify(self, type, text):
        self.emit('notify', json.dumps({'type': type, 'text': text}))

    def switch_tab(self, tab):
        self.ui._sections_root.on_switch(tab.uid)

    def launch(self, intent, **data):
        for section in self.ui._sections:
            for handler in section._intents:
                if handler == intent:
                    section._intents[handler](**data)
                    return

    def get_section(self, cls):
        for section in self.ui._sections:
            if section.__class__ == cls:
                return section

    def ui_watcher(self):
        # Sends UI updates periodically
        while True:
            if self.ui.has_updates():
                self.send_update_request()
                gevent.sleep(0.5)
            gevent.sleep(0.2)


@plugin
class SectionPermissions (PermissionProvider):
    def get_name(self):
        return _('Section access')

    def get_permissions(self):
        # Generate permission set on-the-fly
        return [
            ('section:%s' % x.__name__, x.__name__)
            for x in SectionPlugin.get_classes()
        ]


@p('username')
@plugin
class MainPage (UIElement, BasePlugin):
    typeid = 'main:page'

    def on_feedback(self, email, text):
        ajenti.feedback.send_feedback(email, text)
        self.context.notify('info', _('Feedback sent!'))


@p('name')
@plugin
class SectionsCategory (UIElement):
    typeid = 'main:sections_category'


@plugin
class SectionsRoot (UIElement):
    typeid = 'main:sections_root'
    category_order = {
        '': 0,
        'System': 50,
        'Tools': 60,
        'Software': 80,
        'Other': 99
    }

    def init(self):
        self.categories = {}
        self.startup_crashes = []

        profile('Starting plugins')

        for cls in SectionPlugin.get_classes():
            try:
                UserManager.get().require_permission('section:%s' % cls.__name__)

                try:
                    profile('Starting %s' % cls.__name__)
                    cat = cls.new(self.ui)
                    profile_end()
                    self.append(cat)
                except SecurityError:
                    pass
                except Exception, e:
                    e.traceback = traceback.format_exc(e)
                    self.startup_crashes.append(e)
            except SecurityError:
                pass

        profile_end()

        def category_order(x):
            order = 98
            if x.category in self.category_order:
                order = self.category_order[x.category]
            return (order, x.order, x.title)

        self.children = sorted(self.children, key=category_order)
        if len(self.children) > 0:
            self.on_switch(self.children[0].uid)
        #self.on('switch', self.on_switch)

    def on_switch(self, uid):
        for child in self.children:
            child.active = child.uid == uid
            if child.active:
                child.broadcast('on_page_load')
            child.visible = child.active
        self.invalidate()
