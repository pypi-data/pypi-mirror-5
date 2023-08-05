#!/usr/bin/env python
import warnings as _warnings
_warnings.resetwarnings()
_warnings.filterwarnings('error')

from tdi import html

template = html.from_string("""
<node tdi="item">
    <znode tdi:overlay="foo">
        <ynode tdi="subnested"></ynode>
    </znode>
</node>
""".lstrip())

class Model(object):
    def render_subnested(self, node):
        node.content = u"yeah."

model = Model()
template.render(model, startnode="item.subnested")
print
