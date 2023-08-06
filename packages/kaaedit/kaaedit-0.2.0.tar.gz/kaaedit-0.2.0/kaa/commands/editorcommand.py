import re
import subprocess
import unicodedata
import pyjf3
import kaa
from kaa.command import Commands, command, is_enable, norec, norerun
from kaa import document
from kaa.filetype.default import modebase
from gappedbuf import re as gre


class CursorCommands(Commands):
    @command('cursor.right')
    @norerun
    def right(self, wnd):
        wnd.cursor.right()

    @command('cursor.left')
    @norerun
    def left(self, wnd):
        wnd.cursor.left()

    @command('cursor.up')
    @norerun
    def up(self, wnd):
        wnd.cursor.up()

    @command('cursor.down')
    @norerun
    def down(self, wnd):
        wnd.cursor.down()

    @command('cursor.word-right')
    @norerun
    def word_right(self, wnd):
        wnd.cursor.right(word=True)

    @command('cursor.word-left')
    @norerun
    def word_left(self, wnd):
        wnd.cursor.left(word=True)

    @command('cursor.pagedown')
    @norerun
    def pagedown(self, wnd):
        wnd.cursor.pagedown()

    @command('cursor.pageup')
    @norerun
    def pageup(self, wnd):
        wnd.cursor.pageup()

    @command('cursor.home')
    @norerun
    def home(self, wnd):
        wnd.cursor.home()

    @command('cursor.end')
    @norerun
    def end(self, wnd):
        wnd.cursor.end()

    @command('cursor.top-of-file')
    @norerun
    def top(self, wnd):
        wnd.cursor.tof()

    @command('cursor.end-of-file')
    @norerun
    def last(self, wnd):
        wnd.cursor.eof()

    @command('cursor.go-to-line')
    @norerun
    @norec
    def go_to_line(self, wnd):
        def callback(w, s):
            s = s.strip()
            try:
                lineno = int(s)
            except ValueError as e:
                kaa.app.messagebar.set_message(str(e))
                return

            if lineno == 0 or lineno > wnd.document.buf.lineno.linecount():
                kaa.app.messagebar.set_message('Enter valid line number.')
                return

            pos = wnd.document.get_lineno_pos(lineno)
            tol = wnd.document.gettol(pos)
            wnd.cursor.setpos(wnd.cursor.adjust_nextpos(wnd.cursor.pos, tol))

            popup = w.get_label('popup')
            popup.destroy()


        def filter(wnd, s):
            return re.match(r'\d*', s).group()

        from kaa.ui.inputline import inputlinemode
        doc = inputlinemode.InputlineMode.build('Line number:', callback, filter=filter)
        kaa.app.messagebar.set_message("Enter line number")

        kaa.app.show_dialog(doc)


class ScreenCommands(Commands):
    @command('screen.selection.begin')
    @norerun
    def selection_begin(self, wnd):
        wnd.screen.selection.start_selection(wnd.cursor.pos)

    @command('screen.selection.set-end')
    @norerun
    def selection_set_end(self, wnd):
        wnd.screen.selection.set_end(wnd.cursor.pos)

    @command('screen.selection.clear')
    @norerun
    def selection_clear(self, wnd):
        wnd.screen.selection.clear()

    @command('screen.selection.all')
    @norerun
    def select_all(self, wnd):
        f = wnd.cursor.adjust_nextpos(wnd.cursor.pos, 0)
        t = wnd.cursor.adjust_nextpos(wnd.cursor.pos, wnd.document.endpos())
        wnd.screen.selection.set_range(f, t)

    @command('screen.selection.curline')
    @norerun
    def select_cur_line(self, wnd):
        tol = wnd.cursor.adjust_nextpos(
                wnd.cursor.pos,
                wnd.document.gettol(wnd.cursor.pos))
        eol = wnd.cursor.adjust_nextpos(
                wnd.cursor.pos,
                wnd.document.geteol(tol))

        wnd.screen.selection.set_range(tol, eol)

    @command('screen.selection.curword')
    @norerun
    def select_cur_word(self, wnd):
        f, t = wnd.document.mode.get_word_at(wnd.cursor.pos)

        f = wnd.cursor.adjust_nextpos(wnd.cursor.pos, f)
        t = wnd.cursor.adjust_nextpos(wnd.cursor.pos, t)

        wnd.screen.selection.set_range(f, t)

    @command('screen.selection.expand_sel')
    @norerun
    @norec
    def expand_sel(self, wnd):
        mode = wnd.document.mode
        keys = wnd.editmode.last_command_keys
        L = len(keys)

        if L >= 3 and keys[-1] == keys[-2] == keys[-3]:
            self.select_all(wnd)
            if kaa.app.macro.recording:
                kaa.app.macro.record(self.select_all)

        elif L >= 2 and (keys[-1] == keys[-2]):
            self.select_cur_line(wnd)
            if kaa.app.macro.recording:
                kaa.app.macro.record(self.select_cur_line)

        else:
            self.select_cur_word(wnd)
            if kaa.app.macro.recording:
                kaa.app.macro.record(self.select_cur_word)

    @command('screen.lineselection.begin')
    @norerun
    def lineselection_begin(self, wnd):
        tol = wnd.cursor.adjust_nextpos(wnd.document.gettol(wnd.cursor.pos))
        wnd.screen.selection.start_selection(tol)

    @command('screen.lineselection.set-end')
    @norerun
    def lineselection_set_end(self, wnd):
        f = wnd.screen.selection.start
        if f is None:
            self.select_cur_line(wnd)
        else:
            pos = wnd.cursor.pos
            if pos < f:
                tol = wnd.cursor.adjust_nextpos(
                        wnd.document.gettol(pos))
                wnd.screen.selection.set_end(tol)
            else:
                eol = wnd.cursor.adjust_nextpos(
                        wnd.document.geteol(pos))
                wnd.screen.selection.set_end(eol)


class EditCommands(Commands):
    (UNDO_INSERT,
     UNDO_REPLACE,
     UNDO_DELETE) = range(3)

    def on_edited(self, wnd):
        wnd.document.mode.on_edited(wnd)

    def insert_string(self, wnd, pos, s, update_cursor=True):
        """Insert string"""

        cur_pos = wnd.cursor.pos

        wnd.document.insert(pos, s)

        if update_cursor:
            wnd.cursor.setpos(wnd.cursor.pos+len(s))
            wnd.cursor.savecol()

        if wnd.document.undo:
            wnd.document.undo.add(self.UNDO_INSERT, pos, s,
                                  cur_pos, wnd.cursor.pos)

        self.on_edited(wnd)

    def replace_string(self, wnd, pos, posto, s, update_cursor=True):
        """Replace string"""

        cur_pos = wnd.cursor.pos

        deled = wnd.document.gettext(pos, posto)
        wnd.document.replace(pos, posto, s)

        if update_cursor:
            wnd.cursor.setpos(pos+len(s))
            wnd.cursor.savecol()

        if wnd.document.undo:
            wnd.document.undo.add(self.UNDO_REPLACE, pos, posto, s,
                                  deled, cur_pos, wnd.cursor.pos)

        self.on_edited(wnd)

    def delete_string(self, wnd, pos, posto, update_cursor=True):
        """Delete string"""

        cur_pos = wnd.cursor.pos

        if pos < posto:
            deled = wnd.document.gettext(pos, posto)
            wnd.document.delete(pos, posto)

            if update_cursor:
                wnd.cursor.setpos(pos)
                wnd.cursor.savecol()

            if wnd.document.undo:
                wnd.document.undo.add(self.UNDO_DELETE, pos, posto, deled,
                                      cur_pos, wnd.cursor.pos)
            self.on_edited(wnd)

    def put_string(self, wnd, s):
        s = wnd.document.mode.filter_string(wnd, s)

        sel = wnd.screen.selection.get_range()
        wnd.screen.selection.clear()
        if sel:
            f, t = sel
            self.replace_string(wnd, f, t, s)
        else:
            self.insert_string(wnd, wnd.cursor.pos, s)

    def delete_sel(self, wnd):
        sel = wnd.screen.selection.get_range()
        wnd.screen.selection.clear()
        if sel:
            f, t = sel
            self.delete_string(wnd, f, t)
            return True

    @command('edit.delete')
    def delete(self, wnd):
        if self.delete_sel(wnd):
            return

        pos = wnd.cursor.pos
        nextpos = wnd.document.get_nextpos(pos)
        nextpos = wnd.cursor.adjust_nextpos(pos, nextpos)
        if pos < nextpos:
            self.delete_string(wnd, pos, nextpos)

    @command('edit.delete.word')
    def delete_word(self, wnd):
        if self.delete_sel(wnd):
            return

        pos = wnd.cursor.pos
        wnd.cursor.right(word=True)
        nextpos = wnd.cursor.pos
        if pos < nextpos:
            self.delete_string(wnd, pos, nextpos)

    @command('edit.delete.line')
    def delete_line(self, wnd):
        if self.delete_sel(wnd):
            return

        pos = wnd.cursor.pos
        nextpos = wnd.cursor.adjust_nextpos(pos, wnd.document.find_newline(pos))
        if pos < nextpos:
            self.delete_string(wnd, pos, nextpos)

    @command('edit.delete.currentline')
    def delete_currentline(self, wnd):
        if self.delete_sel(wnd):
            return

        pos = wnd.cursor.pos
        f = wnd.cursor.adjust_nextpos(pos, wnd.document.gettol(pos))
        t = wnd.cursor.adjust_nextpos(pos, wnd.document.geteol(f))

        if f < t:
            self.delete_string(wnd, f, t)

    @command('edit.backspace')
    def backspace(self, wnd):
        if self.delete_sel(wnd):
            return

        pos = wnd.cursor.pos
        prevpos = wnd.cursor.adjust_nextpos(
            pos, wnd.document.get_prevpos(pos))
        if prevpos < pos:
            if pos == wnd.screen.pos:
                # locate cursor before delete to scroll half page up
                wnd.cursor.setpos(prevpos)

            self.delete_string(wnd, prevpos, pos)

    @command('edit.backspace.word')
    def backspace_word(self, wnd):
        if self.delete_sel(wnd):
            return

        pos = wnd.cursor.pos
        wnd.cursor.left(word=True)
        prevpos = wnd.cursor.pos
        if prevpos < pos:
            if prevpos < wnd.screen.pos:
                # locate cursor before delete to scroll half page up
                wnd.cursor.setpos(prevpos)

            self.delete_string(wnd, prevpos, pos)

    @command('edit.newline')
    @norerun
    def newline(self, wnd):
        if not wnd.document.mode.auto_indent:
            self.put_string(wnd, '\n')
            return

        wnd.screen.selection.clear()
        indent = wnd.document.mode.on_auto_indent(wnd)

    def get_line_sel(self, wnd):
        doc = wnd.document
        sel = wnd.screen.selection.get_range()
        if not sel:
            f = t = wnd.cursor.pos
        else:
            f, t = sel

        tol =  doc.gettol(f)

        t_tol =  doc.gettol(t)
        if t != t_tol:
            eol = doc.geteol(t)
        else:
            eol = t

        return tol, eol

    def _indent_line(self, wnd, pos):
        mode = wnd.document.mode
        f, t = mode.get_indent_range(pos)
        if pos > t:
            self.put_string(wnd, '\t')
            return

        if f != t:
            cols = mode.calc_cols(f, t)
        else:
            cols = 0

        s = mode.build_indent_str(cols+mode.indent_width)
        self.replace_string(wnd, f, t, s, True)

    @command('edit.indent')
    def indent(self, wnd):
        if not wnd.screen.selection.is_selected():
            self._indent_line(wnd, wnd.cursor.pos)
            return

        doc = wnd.document
        tol, eol = doc.mode.get_line_sel(wnd)
        wnd.screen.selection.set_range(tol, eol)

        wnd.document.undo.beginblock()
        try:
            mode = wnd.document.mode
            while tol < wnd.screen.selection.end:
                f, t = mode.get_indent_range(tol)
                if f != t:
                    cols = mode.calc_cols(f, t)
                else:
                    cols = 0

                s = mode.build_indent_str(cols+mode.indent_width)
                self.replace_string(wnd, f, t, s, False)
                tol = doc.geteol(tol)
        finally:
            wnd.document.undo.endblock()

        wnd.cursor.setpos(wnd.screen.selection.start)
        wnd.cursor.savecol()

    def _dedent_line(self, wnd, pos):
        mode = wnd.document.mode
        f, t = mode.get_indent_range(pos)
        if f != t:
            cols = mode.calc_cols(f, t)
        else:
            cols = 0

        s = mode.build_indent_str(max(0, cols-mode.indent_width))
        self.replace_string(wnd, f, t, s, True)

    @command('edit.dedent')
    def dedent(self, wnd):
        if not wnd.screen.selection.is_selected():
            self._dedent_line(wnd, wnd.cursor.pos)
            return

        doc = wnd.document
        tol, eol = doc.mode.get_line_sel(wnd)
        wnd.screen.selection.set_range(tol, eol)

        wnd.document.undo.beginblock()
        try:
            mode = wnd.document.mode
            while tol < wnd.screen.selection.end:
                f, t = mode.get_indent_range(tol)
                if f != t:
                    cols = mode.calc_cols(f, t)
                else:
                    cols = 0

                if cols:
                    s = mode.build_indent_str(max(0, cols-mode.indent_width))
                    self.replace_string(wnd, f, t, s, False)

                tol = doc.geteol(tol)
        finally:
            wnd.document.undo.endblock()
        wnd.cursor.setpos(wnd.screen.selection.start)
        wnd.cursor.savecol()

    def _undo(self, wnd, rec):
        (action, args, kwargs) = rec
        if action == self.UNDO_INSERT:
            pos, s, cur_pos, newpos = args
            wnd.document.delete(pos, pos+len(s))
            return cur_pos
        elif action == self.UNDO_REPLACE:
            pos, posto, s, deled, cur_pos, newpos = args
            wnd.document.replace(pos, pos+len(s), deled)
            return cur_pos
        else:
            pos, posto, deled, cur_pos, newpos = args
            wnd.document.insert(pos, deled)

        return cur_pos

    @command('edit.undo')
    @norerun
    def undo(self, wnd):
        if wnd.document.undo.can_undo():
            wnd.screen.selection.clear()
            pos = None
            for rec in wnd.document.undo.undo():
                pos = self._undo(wnd, rec)

            if pos is not None:
                wnd.cursor.setpos(pos)
                wnd.cursor.savecol()

            self.on_edited(wnd)

    def _redo(self, wnd, rec):
        (action, args, kwargs) = rec
        if action == self.UNDO_INSERT:
            pos, s, cur_pos, newpos = args
            wnd.document.insert(pos, s)
            return newpos
        elif action == self.UNDO_REPLACE:
            pos, posto, s, deled, cur_pos, newpos = args
            wnd.document.replace(pos, posto, s)
            return pos
        else:
            pos, posto, deled, cur_pos, newpos = args
            wnd.document.delete(pos, posto)

        return newpos

    @command('edit.redo')
    @norerun
    def redo(self, wnd):
        if wnd.document.undo.can_redo():
            wnd.screen.selection.clear()
            pos = None
            for rec in wnd.document.undo.redo():
                pos = self._redo(wnd, rec)

            if pos is not None:
                wnd.cursor.setpos(pos)
                wnd.cursor.savecol()

            self.on_edited(wnd)

    @command('edit.copy')
    def copy(self, wnd):
        sel = wnd.screen.selection.get_range()
        if sel:
            f, t = sel
            kaa.app.clipboard = wnd.document.gettext(f, t)

    @command('edit.cut')
    def cut(self, wnd):
        self.copy(wnd)
        self.delete_sel(wnd)
        wnd.screen.selection.clear()

    @command('edit.paste')
    def paste(self, wnd):
        if kaa.app.clipboard:
            self.put_string(wnd, kaa.app.clipboard)
            wnd.screen.selection.clear()

    @command('edit.conv.upper')
    def conv_upper(self, wnd):
        sel = wnd.screen.selection.get_range()
        if sel:
            f, t = sel
            self.put_string(wnd, wnd.document.gettext(f, t).upper())
            wnd.screen.selection.clear()

    @command('edit.conv.lower')
    def conv_lower(self, wnd):
        sel = wnd.screen.selection.get_range()
        if sel:
            f, t = sel
            self.put_string(wnd, wnd.document.gettext(f, t).lower())
            wnd.screen.selection.clear()

    @command('edit.conv.nfkc')
    def conv_nfkc(self, wnd):
        sel = wnd.screen.selection.get_range()
        if sel:
            f, t = sel
            text = unicodedata.normalize('NFKC',
                         wnd.document.gettext(f, t).lower())
            self.put_string(wnd, text)
            wnd.screen.selection.clear()

    @command('edit.conv.full-width')
    def conv_fullwidth(self, wnd):
        sel = wnd.screen.selection.get_range()
        if sel:
            f, t = sel
            text = pyjf3.tofull(wnd.document.gettext(f, t).lower())
            self.put_string(wnd, text)
            wnd.screen.selection.clear()

    @command('edit.paste-lines')
    @norerun
    def edit_pastelines(self, wnd):
        from kaa.ui.pastelines import pastelinesmode
        doc = pastelinesmode.PasteLinesMode.build(wnd)

        kaa.app.show_dialog(doc)

    @command('tools.execute-shell-command')
    @norerun
    def execute_shell_command(self, wnd):
        def callback(w, s):
            s = s.strip()
            if s:
                ret = subprocess.check_output(
                    s, stderr=subprocess.STDOUT,
                    shell=True,
                    universal_newlines=True)

                wnd.document.mode.edit_commands.put_string(wnd, ret)
                kaa.app.messagebar.set_message(
                    "{} letters inserted".format(len(ret)))

                popup = w.get_label('popup')
                popup.destroy()

        from kaa.ui.inputline import inputlinemode
        doc = inputlinemode.InputlineMode.build('Shell command:', callback)
        kaa.app.messagebar.set_message("Execute shell command")

        kaa.app.show_dialog(doc)


class CodeCommands(Commands):
    @command('code.region.linecomment')
    def linecomment(self, wnd):
        if not wnd.screen.selection.is_selected():
            tol = wnd.document.gettol(wnd.cursor.pos)
            wnd.document.mode.edit_commands.insert_string(
                    wnd, tol, wnd.document.mode.LINE_COMMENT, 
                    update_cursor=False)
            wnd.cursor.setpos(tol)
            wnd.cursor.savecol()
            return
        else:
            tol, eol = wnd.document.mode.get_line_sel(wnd)
            wnd.screen.selection.set_range(tol, eol)
    
            wnd.document.undo.beginblock()
            try:
                mode = wnd.document.mode
                while tol < wnd.screen.selection.end:
                    wnd.document.mode.edit_commands.insert_string(
                        wnd, tol, wnd.document.mode.LINE_COMMENT, 
                        update_cursor=False)
                    tol = wnd.document.geteol(tol)
            finally:
                wnd.document.undo.endblock()
    
            wnd.cursor.setpos(wnd.screen.selection.start)
            wnd.cursor.savecol()

    def _is_comment_line(self, wnd, pos):
        reobj = gre.compile(r'[ \t]*({})'.format(
                    gre.escape(wnd.document.mode.LINE_COMMENT)))
        return reobj.match(wnd.document.buf, pos)
        
    @command('code.region.unlinecomment')
    def uncomment(self, wnd):
        if not wnd.screen.selection.is_selected():
            tol = wnd.document.gettol(wnd.cursor.pos)
            m = self._is_comment_line(wnd, tol)
            if m:
                f, t = m.span(1)
                wnd.document.mode.edit_commands.delete_string(
                    wnd, f, t)
            return
        else:
            tol, eol = wnd.document.mode.get_line_sel(wnd)
            wnd.screen.selection.set_range(tol, eol)
    
            wnd.document.undo.beginblock()
            try:
                mode = wnd.document.mode
                while tol < wnd.screen.selection.end:
                    m = self._is_comment_line(wnd, tol)
                    if m:
                        f, t = m.span(1)
                        wnd.document.mode.edit_commands.delete_string(
                            wnd, f, t, update_cursor=False)
                    tol = wnd.document.geteol(tol)
            finally:
                wnd.document.undo.endblock()
    
            wnd.cursor.setpos(wnd.screen.selection.start)
            wnd.cursor.savecol()

class MacroCommands(Commands):
    @command('macro.start-record')
    @norec
    @norerun
    def start_record(self, wnd):
        kaa.app.macro.start_record()
        kaa.app.messagebar.update()

    @command('macro.end-record')
    @norec
    @norerun
    def end_record(self, wnd):
        kaa.app.macro.end_record()
        kaa.app.messagebar.update()

    @command('macro.toggle-record')
    @norec
    @norerun
    def toggle_record(self, wnd):
        kaa.app.macro.toggle_record()
        kaa.app.messagebar.update()

    @command('macro.run')
    @norec
    def run_macro(self, wnd):
        if kaa.app.macro.is_recording():
            return
        if not kaa.app.macro.get_commands():
            return

        wnd.document.undo.beginblock()
        try:
            kaa.app.macro.run(wnd)
        finally:
            wnd.document.undo.endblock()


class SearchCommands(Commands):
    @command('search.showsearch')
    @norec
    @norerun
    def showsearch(self, wnd):
        from kaa.ui.searchdlg import searchdlgmode

        buf = document.Buffer()
        doc = document.Document(buf)
        mode = searchdlgmode.SearchDlgMode(target=wnd)
        doc.setmode(mode)
        mode.build_document()

        kaa.app.show_inputline(doc)

    @command('search.showreplace')
    @norec
    @norerun
    def showreplace(self, wnd):
        from kaa.ui.searchdlg import searchdlgmode

        buf = document.Buffer()
        doc = document.Document(buf)
        mode = searchdlgmode.ReplaceDlgMode(target=wnd)
        doc.setmode(mode)
        mode.build_document()

        kaa.app.show_inputline(doc)

    def _show_searchresult(self, wnd, hit):
        if hit:
            f, t = hit.span()
            wnd.cursor.setpos(f)
            wnd.screen.selection.start = f
            wnd.screen.selection.end = t
            kaa.app.messagebar.set_message('found')
        else:
            kaa.app.messagebar.set_message('not found')

    @command('search.next')
    @norerun
    def searchnext(self, wnd):
        if not modebase.SearchOption.LAST_SEARCH:
            return
        if not modebase.SearchOption.LAST_SEARCH.text:
            return
        range = wnd.screen.selection.get_range()
        if range:
            start = range[0]+1
        else:
            start =  wnd.cursor.pos

        ret = wnd.document.mode.search_next(start, modebase.SearchOption.LAST_SEARCH)
        self._show_searchresult(wnd, ret)

        if not ret:
            if start != 0:
                ret = wnd.document.mode.search_next(0, modebase.SearchOption.LAST_SEARCH)
                self._show_searchresult(wnd, ret)

    @command('search.prev')
    @norerun
    def searchprev(self, wnd):
        if not modebase.SearchOption.LAST_SEARCH:
            return
        if not modebase.SearchOption.LAST_SEARCH.text:
            return
        range = wnd.screen.selection.get_range()
        if range:
            start = range[1]-1
        else:
            start =  wnd.cursor.pos

        ret = wnd.document.mode.search_prev(start, modebase.SearchOption.LAST_SEARCH)
        self._show_searchresult(wnd, ret)

        if not ret:
            if start != wnd.document.endpos():
                ret = wnd.document.mode.search_prev(wnd.document.endpos(),
                                                    modebase.SearchOption.LAST_SEARCH)
                self._show_searchresult(wnd, ret)

    @command('search.showgrep')
    @norec
    @norerun
    def showgrep(self, wnd):
        from kaa.ui.grep import grepdlgmode

        buf = document.Buffer()
        doc = document.Document(buf)
        mode = grepdlgmode.GrepDlgMode(wnd)
        doc.setmode(mode)
        mode.build_document()

        kaa.app.show_dialog(doc)


class RerunCommand(Commands):
    @command('command.rerun')
    @norerun
    def reruncommand(self, wnd):
        mode = wnd.document.mode
        for commandid in kaa.app.lastcommands:
            is_available, command = mode.get_command(commandid)
            if not command:
                msg = 'command {!r} is not registered.'.format(commandid)
                kaa.app.messagebar.set_message(msg)
                kaa.log.error(msg)
                return
            command(wnd)

