#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py's CheckBox control (uses wx.CheckBox)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"  # where applicable

# Initial implementation was based on PythonCard's CehckBox component, 
# but redesigned and overhauled a lot (specs renamed, events refactorized, etc.)

import wx
from ..event import FormEvent
from ..component import Control, Spec, EventSpec, InitSpec
from .. import images


class CheckBox(Control):
    "A check box."
    
    _wx_class = wx.CheckBox
    _style = wx.CLIP_SIBLINGS | wx.NO_FULL_REPAINT_ON_RESIZE
    _image = images.checkbox
        
    value = Spec(lambda self: self.wx_obj.GetValue(), 
                   lambda self, value: self.wx_obj.SetValue(value), 
                   default=False, type="boolean")
    label = InitSpec(lambda self: self.wx_obj.GetLabel(), 
                     lambda self, value: self.wx_obj.SetLabel(value),
                     type="string", default="Option")

    onclick = EventSpec('click', binding=wx.EVT_CHECKBOX, kind=FormEvent)


if __name__ == "__main__":
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    c = CheckBox(frame, name="chkTest", border='none', label="Check me!")
    assert c.get_parent() is frame
    assert c.name == "chkTest"
    assert c.label == "Check me!"
    from pprint import pprint
    # assign some event handlers:
    c.onclick = lambda event: pprint("click: %s" % event.target.value)
    frame.Show()
    app.MainLoop()
