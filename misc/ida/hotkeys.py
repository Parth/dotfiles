import webbrowser
import ida_kernwin as kw


def google_highlighted():
    """gets textual representation of currently selected identifier
    from any current IDA view, opens a new browser tab and googles for it
    cerdit: https://github.com/patois
    """

    r = kw.get_highlight(kw.get_current_viewer())
    if r:
        webbrowser.open("https://google.com/search?q=%s" % r[0],new=2)
    
kw.add_hotkey("Ctrl-Shift-F", google_highlighted)
