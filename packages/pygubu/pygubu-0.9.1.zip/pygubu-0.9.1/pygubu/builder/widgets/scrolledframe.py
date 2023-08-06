from __future__ import unicode_literals

from pygubu.builder.builderobject import *
from pygubu.widgets.scrolledframe import ScrolledFrame


class TTKScrolledFrameBO(BuilderObject):
    class_ = ScrolledFrame
    container = False
    maxchildren = 1
    allowed_children = ('tk.Frame', 'ttk.Frame' )
    properties = ['class_', 'cursor', 'height', 'padding',
            'relief', 'style', 'takefocus', 'width', 'scrolltype']
    ro_properties = ('class_', 'scrolltype')

    def get_child_master(self):
        return self.widget.innerframe


register_widget('pygubu.builder.widgets.scrolledframe', TTKScrolledFrameBO,
    'ScrolledFrame', ('Pygubu Widgets', 'ttk'))
