#!/usr/bin/python
"""Find in files and replace strings in many files."""

__metaclass__ = type

__all__ = [
    'extract_match',
    'find_files',
    'find_matches',
    'Finder',
    ]

import mimetypes
import os
import re
import sys
from optparse import OptionParser

import gobject
import gtk

from gdp import PluginMixin


def find_matches(root_dir, file_pattern, match_pattern, substitution=None):
    """Iterate a summary of matching lines in a file."""
    match_re = re.compile(match_pattern)
    for file_path in find_files(root_dir, file_pattern=file_pattern):
        summary = extract_match(
            file_path, match_re, substitution=substitution)
        if summary:
            yield summary


def find_files(root_dir, skip_dir_pattern='^[.]', file_pattern='.*'):
    """Iterate the matching files below a directory."""
    skip_dir_re = re.compile(r'^.*%s' % skip_dir_pattern)
    file_re = re.compile(r'^.*%s' % file_pattern)
    for path, subdirs, files in os.walk(root_dir):
        subdirs[:] = [dir_ for dir_ in subdirs
                      if skip_dir_re.match(dir_) is None]
        for file_ in files:
            file_path = os.path.join(path, file_)
            if os.path.islink(file_path):
                continue
            mime_type, encoding_ = mimetypes.guess_type(file_)
            if mime_type is None or 'text/' in mime_type:
                if file_re.match(file_path) is not None:
                    yield file_path


def extract_match(file_path, match_re, substitution=None):
    """Return a summary of matches in a file."""
    lines = []
    content = []
    match = None
    file_ = open(file_path, 'r')
    try:
        for lineno, line in enumerate(file_):
            match = match_re.search(line)
            if match:
                lines.append(
                    {'lineno' : lineno + 1, 'text' : line.strip(),
                     'match': match})
                if substitution is not None:
                    line = match_re.sub(substitution, line)
            if substitution is not None:
                content.append(line)
    finally:
        file_.close()
    if lines:
        if substitution is not None:
            file_ = open(file_path, 'w')
            try:
                file_.write(''.join(content))
            finally:
                file_.close()
        return {'file_path' : file_path, 'lines' : lines}
    return None


class Finder(PluginMixin):
    """Find and replace content in files."""

    def __init__(self, gedit, window):
        self.initialize(gedit)
        self.window = window
        self.widgets = gtk.glade.XML(
            '%s/gdp.glade' % os.path.dirname(__file__), root='find_panel')
        self.setup_widgets()
        self.find_panel = self.widgets.get_widget('find_panel')
        panel = window.get_bottom_panel()
        icon = gtk.image_new_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU)
        panel.add_item(self.find_panel, 'Find in files', icon)

    def setup_widgets(self):
        """Setup the widgets with default data."""
        self.widgets.signal_autoconnect(self.glade_callbacks)
        combobox = self.widgets.get_widget('match_pattern_combobox')
        liststore = gtk.ListStore(gobject.TYPE_STRING)
        liststore.set_sort_column_id(0, gtk.SORT_ASCENDING)
        combobox.set_model(liststore)
        combobox.set_text_column(0)

    @property
    def glade_callbacks(self):
        """The dict of callbacks for the glade widgets."""
        return {
            'on_find_in_files' : self.on_find_in_files,
            }

    def update_match_text(self, combobox, text):
        """Update the match text combobox."""
        is_unique = True
        for row in iter(combobox.get_model()):
            if row[0] == text:
                is_unique = False
                break
        if is_unique:
            combobox.append_text(text)

    def show(self, data):
        """Show the finder pane."""
        panel = self.window.get_bottom_panel()
        panel.activate_item(self.find_panel)
        panel.props.visible = True

    def on_find_in_files(self, widget=None):
        """Find and present the matches."""
        combobox = self.widgets.get_widget('match_pattern_combobox')
        text = combobox.get_active_text()
        self.update_match_text(combobox, text)
        if not self.widgets.get_widget('re_checkbox').get_active():
            text = re.escape(text)
        if not self.widgets.get_widget('match_case_checkbox').get_active():
            text = '(?i)%s' % text
        # XXX sinzui 2009-08-28: Run this as a log until the UI is finished.
        file_path = os.path.abspath('./_find.log')
        try:
            log = open(file_path, 'w')
            log.write("Looking for [%s] in %s:\n" % (text, '.'))
            for summary in find_matches('.', '.', text, substitution=None):
                log.write("\n%(file_path)s\n" % summary)
                for line in summary['lines']:
                    log.write("    %(lineno)4s: %(text)s\n" % line)
        finally:
            log.close()
        uri = 'file://%s' % file_path
        self.open_doc(uri)
        self.window.set_active_tab(self.window.get_tab_from_uri(uri))


def get_option_parser():
    """Return the option parser for this program."""
    usage = "usage: %prog [options] root_dir file_pattern match"
    parser = OptionParser(usage=usage)
    parser.add_option(
        "-s", "--substitution", dest="substitution",
        help="The substitution string (may contain \\[0-9] match groups).")
    parser.set_defaults(substitution=None)
    return parser


def main(argv=None):
    """Run the command line operations."""
    if argv is None:
        argv = sys.argv
    parser = get_option_parser()
    (options, args) = parser.parse_args(args=argv[1:])

    root_dir = args[0]
    file_pattern = args[1]
    match_pattern = args[2]
    substitution = options.substitution
    print "Looking for [%s] in files like %s under %s:" % (
        match_pattern, file_pattern, root_dir)
    for summary in find_matches(
        root_dir, file_pattern, match_pattern, substitution=substitution):
        print "\n%(file_path)s" % summary
        for line in summary['lines']:
            print "    %(lineno)4s: %(text)s" % line


if __name__ == '__main__':
    sys.exit(main())
