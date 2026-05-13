#!/usr/bin/env python3
"""
Watcher de arquivos para sessões ativas do DevTracker.

Uso: python watcher.py <session_id> <path>
Salva PID em /tmp/devtracker_watcher.pid e registra Events do tipo
file_change para cada arquivo modificado no diretório monitorado.
"""
import os
import sys
import time
import signal

PID_FILE = '/tmp/devtracker_watcher.pid'

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devtracker.settings')

import django
django.setup()

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from tracker.models import Session, Event


IGNORED_EXTENSIONS = {'.pyc', '.pyo', '.swp', '.swo', '.tmp', '.lock'}
IGNORED_DIRS = {'__pycache__', '.git', '.venv', 'node_modules', '.mypy_cache'}


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, session_id):
        self.session_id = session_id

    def on_modified(self, event):
        if event.is_directory:
            return
        self._record(event.src_path)

    def on_created(self, event):
        if event.is_directory:
            return
        self._record(event.src_path)

    def _record(self, path):
        parts = path.split(os.sep)
        if any(d in IGNORED_DIRS for d in parts):
            return
        ext = os.path.splitext(path)[1].lower()
        if ext in IGNORED_EXTENSIONS:
            return
        try:
            session = Session.objects.get(pk=self.session_id, ended_at__isnull=True)
            Event.objects.create(
                session=session,
                event_type='file_change',
                metadata={'file': path, 'extension': ext or '(none)'},
            )
        except Session.DoesNotExist:
            # Sessão encerrada — para o observer
            os.kill(os.getpid(), signal.SIGTERM)


def main():
    if len(sys.argv) < 3:
        print('Uso: watcher.py <session_id> <path>', file=sys.stderr)
        sys.exit(1)

    session_id = int(sys.argv[1])
    watch_path = sys.argv[2]

    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    handler = FileChangeHandler(session_id)
    observer = Observer()
    observer.schedule(handler, watch_path, recursive=True)
    observer.start()

    def _stop(signum, frame):
        observer.stop()

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    try:
        observer.join()
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)


if __name__ == '__main__':
    main()
