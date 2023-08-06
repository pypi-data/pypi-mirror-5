import os, importlib, sqlite3
import kaa
from kaa import consts

class KaaHistoryStorage:
    def __init__(self, filename):
        self.filename = filename
        self.conn = sqlite3.connect(filename)
        
    def close(self):
        self.conn.close()
        
    def add_history(self, history):
        history.set_storage(self)

    

class History:
    MAX_HISTORY = 999

    def __init__(self, name, storage):
        self.name = name
        self.table_name = 'hist_'+self.name
        self.storage = None

        storage.add_history(self)
        
    def close(self):
        ret = self.storage.conn.execute('''
            SELECT id FROM {} ORDER BY id DESC LIMIT ?
            '''.format(self.table_name), (self.MAX_HISTORY, ))
        recs =[value for value in ret]
        if recs:
            last, = recs[-1]
            self.storage.conn.execute('''
                DELETE FROM {} WHERE id < ?
                '''.format(self.table_name), (last,))
            self.storage.conn.commit()
            
    def set_storage(self, storage):
        storage.conn.execute('''
            CREATE TABLE IF NOT EXISTS {}
                (id INTEGER PRIMARY KEY,
                value TEXT)'''.format(self.table_name))
        self.storage = storage

    def add(self, value):
        if not value:
            return

        ret = self.storage.conn.execute('''
            DELETE FROM {} WHERE value = ?'''.format(self.table_name),
            (value, ))

        self.storage.conn.execute('''
            INSERT INTO {}(value) VALUES(?)'''.format(self.table_name),
            (value,))

        self.storage.conn.commit()

    def get(self):
        ret = self.storage.conn.execute('''
            SELECT value FROM {} ORDER BY id DESC LIMIT ?
            '''.format(self.table_name),
            (self.MAX_HISTORY,))
        return [value for value, in ret]

class Config:
    FILETYPES = [
        'kaa.filetype.default',
        'kaa.filetype.python',
        'kaa.filetype.html',
        'kaa.filetype.javascript',
        'kaa.filetype.css',
    ]

    DEFAULT_NEWLINE = 'auto'
    DEFAULT_ENCODING = 'utf-8'

    def __init__(self):
        kaadir = os.path.abspath(
                 os.path.expandvars(
                 os.path.expanduser(consts.KAA_DIR)))

        if not os.path.exists(kaadir):
            os.makedirs(kaadir)

        logdir = os.path.join(kaadir, consts.LOGDIR)
        if not os.path.exists(logdir):
            os.mkdir(logdir)

        histdir = os.path.join(kaadir, consts.HISTDIR)
        if not os.path.exists(histdir):
            os.mkdir(histdir)

        userdir = os.path.join(kaadir, 'kaa')
        if not os.path.exists(userdir):
            os.mkdir(userdir)

        self.KAADIR = kaadir
        self.LOGDIR = logdir
        self.HISTDIR = histdir

    def init_history(self):
        self.hist_storage = KaaHistoryStorage(
            os.path.join(self.HISTDIR, consts.HIST_DBNAME))

        self.hist_files = History('files', self.hist_storage)
        self.hist_dirs = History('dirs', self.hist_storage)
        self.hist_searchstr = History('searchstr', self.hist_storage)
        self.hist_replstr = History('replstr', self.hist_storage)
        self.hist_grepstr = History('grepstr', self.hist_storage)
        self.hist_grepdir = History('grepdir', self.hist_storage)
        self.hist_grepfiles = History('grepfiles', self.hist_storage)

    def get_mode_packages(self):
        for pkgname in self.FILETYPES:
            try:
                pkg = importlib.import_module(pkgname)
            except Exception:
                kaa.log.exception('Error loading filetype: '+repr(pkgname))
            else:
                yield pkg
   