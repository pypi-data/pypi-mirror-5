from ajenti.api import *
from ajenti.ui import *


@p('title')
@p('icon', default=None)
@p('order', default=99, doc='Sorting weight, light plugins end up higher')
@p('category', default='Other', doc='Section category name')
@p('active', default=False)
@p('plain', default=False)
@interface
class SectionPlugin (BasePlugin, UIElement):
    """
    A base class for section plugins visible on the left in the UI. Inherits :class:`ajenti.ui.UIElement`
    """

    typeid = 'main:section'
    _intents = {}

    def init(self):
        for k, v in self.__class__.__dict__.iteritems():
            if hasattr(v, '_intent'):
                self._intents[v._intent] = getattr(self, k)

    def activate(self):
        """
        Activate this section
        """
        self.context.endpoint.switch_tab(self)

    def on_page_load(self):
        """
        Called when this section becomes active, or the page is reloaded
        """
        pass


def intent(id):
    """
    Registers this method as an intent with given ID
    """
    def decorator(fx):
        fx._intent = id
        return fx
    return decorator
