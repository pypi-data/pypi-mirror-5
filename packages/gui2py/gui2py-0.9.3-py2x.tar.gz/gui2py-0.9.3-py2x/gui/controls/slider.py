#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py's Slider control, similar to a scrollbar in other libs (uses wx.Slider)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"  # where applicable

# Initial implementation was based on PythonCard's List component, 
# but redesigned and overhauled a lot (specs renamed, events refactorized, etc.)

import wx
from ..component import Control, Spec, EventSpec, InitSpec, StyleSpec
from ..event import FormEvent
from .. import images


class Slider(Control):
    "A control with a handle which can be pulled back & forth (~ scroll bar)"

    _wx_class = wx.Slider
    _style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_SIBLINGS
    _image = images.slider

    
    layout = StyleSpec({'horizontal': wx.SL_HORIZONTAL, 
                        'vertical': wx.SL_VERTICAL},
                        default="horizontal",
                        doc="appareance")
    labels = StyleSpec(wx.SL_LABELS, doc="appareance") 
    ticks = StyleSpec(wx.SL_TICKS, doc="appareance") 
    freq = Spec(lambda self: self.wx_obj.GetTickFreq(),
                lambda self, value: self.wx_obj.SetTickFreq(value),
                default=1,
                ) 
    max = Spec(lambda self: self.wx_obj.GetMax(), 
               lambda self, value: self.wx_obj.SetRange(self.min, value),
               default=100, type="integer",
               doc="Range of the gauge")
    min = Spec(lambda self: self.wx_obj.GetMin(), 
               lambda self, value: self.wx_obj.SetRange(value, self.max),
               default=0, type="integer",
               doc="Range of the gauge")
    value = Spec(lambda self: self.wx_obj.GetValue(), 
                 lambda self, value: self.wx_obj.SetValue(value),
                 default=0, type="integer",
                 doc="Current value (position of the gauge)")

    onclick = EventSpec('click', binding=wx.EVT_SLIDER, kind=FormEvent)


if __name__ == "__main__":
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    s = Slider(frame, name="slider")
    s.onclick = "print event.target.value"
    frame.Show()
    app.MainLoop()
