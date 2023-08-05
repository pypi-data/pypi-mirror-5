#!/usr/bin/env python
import warnings as _warnings
_warnings.resetwarnings()
_warnings.filterwarnings('error')

from tdi import html

template = html.from_string("""
<node tdi="item">
    <node tdi="nested">
        <node tdi="subnested"></node>
    </node><tdi tdi=":-nested">
    </tdi>
</node>
""".lstrip())

class Model(object):
    def render_item(self, node):
        def sep(node):
            node.hiddenelement = False
            node.content = (
                  u'\n        '
                + u'-'.join(map(unicode, node.ctx[1]))
                + u'\n    '
            )
        for subnode, item in node.nested.iterate([1, 2, 3, 4], separate=sep):
            subnode['j'] = item

model = Model()
template.render(model)
