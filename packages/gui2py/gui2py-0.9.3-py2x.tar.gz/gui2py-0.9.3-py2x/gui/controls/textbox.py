#!/usr/bin/python
# -*- coding: utf-8 -*-

"gui2py's TextBox control (uses wx.TextCtrl, wx.lib.masked & wx.DatePickerCtrl)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2013- Mariano Reingart"  # where applicable

# Initial implementation was based on PythonCard's TextField/TextArea component, 
# but redesigned and overhauled a lot (specs renamed, events refactorized, etc.)
# Support for Masked TextCtrl/NumCtrl and DatePicker is completely new

import locale
import decimal
import datetime
import wx
from ..event import FormEvent
from ..component import Control, Spec, EventSpec, InitSpec, StyleSpec
from .. import images 
import  wx.lib.masked as masked


class TextBox(Control):
    "A text field"

    _wx_class = wx.TextCtrl
    _style = wx.CLIP_SIBLINGS | wx.NO_FULL_REPAINT_ON_RESIZE
    _image = images.textbox

    def __init__(self, *args, **kwargs):
        # if mask is given, create a masked control
        if 'mask' in kwargs and kwargs['mask']:
            if all([(ch in ("#", ".")) for ch in kwargs['mask']]):
                self._wx_class = wx_masked_NumCtrl
            elif kwargs['mask'] == 'date':
                self._wx_class = wx_DatePickerCtrl
            else:
                self._wx_class = wx_masked_TextCtrl
                
        elif 'mask' in kwargs:   
            del kwargs['mask']

        Control.__init__(self, *args, **kwargs)
        # sane default for tab caption (in designer)
    
    
    def clear_selection(self):
        if self.can_cut():
            # delete the current selection,
            # if we can't do a Cut we shouldn't be able to delete either
            # which is why i used the test above
            sel = self.replace_selection('')
        else:
            ins = self.get_insertion_point()
            try:
                self.replace(ins, ins + 1, '')
            except:
                pass

    # KEA the methods for retrieving and manipulating the text
    # has to be greatly expanded to match wxPython
    # capabilities or more


    # KEA new methods to mirror wxPython wxTextCtrl capabilities
    def append_text( self, aString ) :
        """Appends the text to the end of the text widget.
        After the text is appended, the insertion point will be at the end
        of the text widget. If this behavior is not desired, the programmer
        should use getInsertionPoint and setInsertionPoint."""
        self.wx_obj.AppendText( aString )

    def can_copy( self ) :
        return self.wx_obj.CanCopy()

    def can_cut( self ) :
        return self.wx_obj.CanCut()

    def can_paste( self ) :
        return self.wx_obj.CanPaste()

    def can_redo( self ) :
        return self.wx_obj.CanRedo()

    def can_undo( self ) :
        return self.wx_obj.CanUndo()

    def clear( self ) :
        self.wx_obj.Clear()

    def copy( self ) :
        self.wx_obj.Copy()

    def cut( self ) :
        self.wx_obj.Cut()

    def discard_edits( self ) :
        self.wx_obj.DiscardEdits()
    
    def get_insertion_point( self ) :
        return self.wx_obj.GetInsertionPoint()

    def get_last_position( self ) :
        return self.wx_obj.GetLastPosition()

    def get_line_length( self, aLineNumber ) :
        return self.wx_obj.GetLineLength( aLineNumber )

    def get_line_text( self, aLineNumber ) :
        return self.wx_obj.GetLineText( aLineNumber )

    def get_selection( self ) :
        return self.wx_obj.GetSelection()

    def get_number_of_lines( self ) :
        return self.wx_obj.GetNumberOfLines()
        
    def set_max_length(self, max):
        "sets the maximum number of characters allowed into the control"
        return self.wx_obj.SetMaxLength(max)

    # KEA rename to getModified?
    def is_modified( self ) :
        """Returns 1 if the text has been modified, 0 otherwise."""
        return self.wx_obj.IsModified()

    # KEA support LoadFile? If so, it only makes sense for TextArea
    # many of the other methods only make sense for the multiline TextArea
    # not TextField and PasswordField

    # KEA OnChar ties into our user code handlers and our events,
    # need to think about this one some more

    # KEA OnDropFiles is windows-specific, if you try and call it under *nix
    # what happens? just an exception?

    def paste( self ) :
        self.wx_obj.Paste()

    def position_to_xy(self, aPosition):
        result = self.wx_obj.PositionToXY(aPosition)
        if len(result) == 2:
            return result
        else:
            # workaround for wxPython 2.3.2.1
            return (result[1], result[2])

    def redo( self ) :
        self.wx_obj.Redo()

    def remove( self, aFrom, aTo ) :
        self.wx_obj.Remove( aFrom, aTo )

    def replace( self, aFrom, aTo, aString ) :
        # KEA workaround for Replace bug, has the side effect of
        # possibly changing the insertion point
        #self._delegate.Replace( aFrom, aTo, aString )
        i = self.wx_obj.GetInsertionPoint()
        self.wx_obj.Remove( aFrom, aTo )
        self.wx_obj.SetInsertionPoint( aFrom )
        self.wx_obj.WriteText( aString )
        self.wx_obj.SetInsertionPoint( i )

    def replace_selection(self, aString, select=0):
        sel = self.GetSelection()
        self.Remove(sel[0], sel[1])
        self.WriteText(aString)
        if select:
            self.SetSelection(sel[0], sel[0] + len(aString))

    # KEA support SaveFile?

    def set_insertion_point( self, aPosition ) :
        self.SetInsertionPoint( aPosition )

    def set_insertion_point_end( self ) :
        self.SetInsertionPointEnd()

    def set_selection( self, aFrom, aTo ) :
        self.SetSelection( aFrom, aTo )

    def show_position( self, aPosition ) :
        self.ShowPosition( aPosition )

    def undo( self ) :
        self.Undo()

    def write_text( self, aString ) :
        self.WriteText( aString )

    def xy_to_position( self, aX, aY ) :
        return self.XYToPosition( aX, aY )

    get_string_selection = lambda self: self.wx_obj.GetStringSelection
    
    def get_string(self, aFrom, aTo):
        return self.GetValue()[aFrom:aTo]

    def _get_mask(self):
        if hasattr(self.wx_obj, "GetMask"):
            return self.wx_obj.GetMask()
        else:
            return None
    
    def _set_mask(self, new_mask):
        if isinstance(self.wx_obj, masked.TextCtrl):
            self.wx_obj.SetMask(new_mask)

    def _get_text(self):
        text = self.wx_obj.GetValue()
        if not isinstance(text, basestring) and text is not None:
            return None     # for safety, do not return a string repr
        else:
            return text
    
    def _set_text(self, new_text):
        self.wx_obj.SetValue(unicode(new_text))

    def _get_value(self):
        return self.wx_obj.GetValue()
    
    def _set_value(self, new_value):
        self.wx_obj.SetValue(new_value)
        
    alignment = StyleSpec({'left': wx.TE_LEFT, 
                           'center': wx.TE_CENTRE,
                           'right': wx.TE_RIGHT},
                           default='left')
    editable = Spec(lambda self: self.wx_obj.IsEditable(), 
                    lambda self, value: self.wx_obj.SetEditable(value),
                    default=True, type="boolean")
    ##text = Spec(_get_text, _set_text, default="", type="text")
    value = Spec(_get_value, _set_value, default="", type="expr",
                 doc="Actual python object (int, float, datetime, decimal...)")
    password = StyleSpec(wx.TE_PASSWORD, default=False)
    multiline = StyleSpec(wx.TE_MULTILINE, default=False)
    hscroll = StyleSpec(wx.HSCROLL, default=False)

    onchange = EventSpec('change', binding=wx.EVT_TEXT, kind=FormEvent)

    mask = InitSpec(_get_mask, _set_mask, type='string', default=None, 
                    doc="template to control allowed user input")


class wx_masked_TextCtrl(masked.TextCtrl):

    def __init__(self, *args, **kwargs):
        # Use local conventions for decimal point and grouping
        lc = locale.localeconv()
        kwargs['useFixedWidthFont'] = False
        kwargs['groupChar'] = lc['mon_thousands_sep'] or ","
        kwargs['decimalChar'] = lc['decimal_point'] or "."
        kwargs['raiseOnInvalidPaste'] = False               # just bell
        masked.TextCtrl.__init__(self, *args, **kwargs) 
        
    def SetValue(self, new_value):
        # to avoid formatting issues, values should not be passed as string!
        try:
            masked.TextCtrl.SetValue(self, new_value)
        except Exception, e:
            # TODO: better exception handling
            print e
    
    def GetValue(self):
        # should return number / date / etc.
        value = masked.TextCtrl.GetValue(self)  # get the text value
        return value


class wx_masked_NumCtrl(masked.NumCtrl):
    
    def __init__(self, *args, **kwargs):
        # Use local conventions for decimal point and grouping
        lc = locale.localeconv()
        kwargs['useFixedWidthFont'] = False
        kwargs['groupChar'] = lc['mon_thousands_sep'] or ','
        kwargs['decimalChar'] = lc['decimal_point'] or '.'
        mask = kwargs['mask']
        del kwargs['mask']
        if '.' not in mask:
            kwargs['fractionWidth'] = 0
            kwargs['integerWidth'] = mask.count("#")
        else:
            kwargs['fractionWidth'] = mask[mask.index("."):].count("#")
            kwargs['integerWidth'] = mask[:mask.index(".")].count("#") 
        kwargs['allowNone'] = True
        kwargs['autoSize'] = False
        #allowNegative = True,
        #useParensForNegatives = False,
        #groupDigits = False,
        #min = None,
        #max = None,
        masked.NumCtrl.__init__(self, *args, **kwargs)

    def GetMask(self):
        fraction_width = self.GetFractionWidth() 
        integer_width = self.GetIntegerWidth()
        if fraction_width:
            return "%s.%s" % ("#" * integer_width, "#" * fraction_width)
        else:
            return "#" * integer_width

    def SetValue(self, new_value):
        # to avoid formatting issues, values should not be passed as string!
        try:
            masked.NumCtrl.SetValue(self, new_value)
        except Exception, e:
            # TODO: better exception handling
            print e


# WORKAROUND as Phoenix moved datetime picker
# (could be useful for WXMAC or similar):
if wx.VERSION < (2, 9, 5):
    DatePickerCtrl = wx.DatePickerCtrl
    DP_STYLE = wx.DP_DROPDOWN | wx.DP_SHOWCENTURY | wx.DP_ALLOWNONE | wx.DP_DEFAULT
else:
    import wx.adv
    DatePickerCtrl = wx.adv.DatePickerCtrl
    DP_STYLE = wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY | wx.adv.DP_ALLOWNONE | wx.adv.DP_DEFAULT

if DatePickerCtrl:
    class wx_DatePickerCtrl(DatePickerCtrl):
    
        def __init__(self, *args, **kwargs):
            del kwargs['mask']
            kwargs['style'] = style = DP_STYLE
            DatePickerCtrl.__init__(self, *args, **kwargs)

        def GetMask(self):
            return "date"

        def SetEditable(self, editable):
            pass # TODO
            
        def IsEditable(self):
            return True # TODO

        def GetValue(self):
            "Convert and return the wx.DateTime to python datetime"
            value = DatePickerCtrl.GetValue(self)
            assert isinstance(value, wx.DateTime) 
            if value is None or not value.IsValid(): 
                return
            else:
                 ymd = map(int, value.FormatISODate().split('-')) 
                 return datetime.date(*ymd)          

        def SetValue(self, new_value):
            "Convert and set the python datetime to wx.DateTime"
            try:
                 assert isinstance(new_value, (datetime.datetime, datetime.date)) 
                 tt = new_value.timetuple() 
                 dmy = (tt[2], tt[1]-1, tt[0]) 
                 DatePickerCtrl.SetValue(self, wx.DateTimeFromDMY(*dmy)) 
            except Exception, e:
                # TODO: better exception handling
                print e

else:

    # TODO: look for a better alternative for wx.DatePickerCtrl (masked?)

    class wx_DatePickerCtrl(wx.TextCtrl):

        def __init__(self, *args, **kwargs):
            del kwargs['mask']
            wx.TextCtrl.__init__(self, *args, **kwargs)

        def GetValue(self):
            "Convert and return the wx.DateTime to python datetime"
            value = wx.TextCtrl.GetValue(self)
            if not value: 
                return
            else:
                 ymd = map(int, value.split('-')) 
                 return datetime.date(*ymd)          

        def SetValue(self, new_value):
            "Convert and set the python datetime to wx.DateTime"
            try:
                 assert isinstance(new_value, (datetime.datetime, datetime.date))
                 wx.TextCtrl.SetValue(self, str(new_value)) 
            except Exception, e:
                # TODO: better exception handling
                print e

    
if __name__ == "__main__":
    import sys
    # basic test until unit_test
    app = wx.App(redirect=False)
    frame = wx.Frame(None)
    t = TextBox(frame, name="txtTest", border=False, text="",
                password='--password' in sys.argv,
                multiline='--multiline' in sys.argv,
                mask='###.##',
                hscroll=True,
                )
    t.value = 1.01
    assert t.get_parent() is frame
    assert t.name == "txtTest"
    print "align", t.alignment
    print "text", t.text
    print "mask", t.mask
    print "password", t.password
    print "multiline", t.multiline
    print "hscroll", t.hscroll
    #assert t.text == "hello world!"
    from pprint import pprint
    # assign some event handlers:
    t.onmousemove = lambda event: pprint("%s %s %s" % (event.name, event.x, event.y))
    t.onmouseleftdown = lambda event: pprint(event.target.append_text("click!"))
    t.onchange = lambda event: pprint("change: %s" % event.target.text)
    frame.Show()
    #print t.value, type(t.value)
    app.MainLoop()    

