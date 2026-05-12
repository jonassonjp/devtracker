import os
import sys
import subprocess

_COMMANDS_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(_COMMANDS_DIR)


def django_setup():
    if _BASE_DIR not in sys.path:
        sys.path.insert(0, _BASE_DIR)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devtracker.settings')
    import django
    django.setup()


def open_pycharm(directory):
    candidates = ['charm', 'pycharm', 'pycharm-professional', 'pycharm-community']

    toolbox_scripts = os.path.expanduser('~/.local/share/JetBrains/Toolbox/scripts')
    if os.path.isdir(toolbox_scripts):
        for name in sorted(os.listdir(toolbox_scripts)):
            if 'pycharm' in name.lower():
                candidates.append(os.path.join(toolbox_scripts, name))

    for cmd in candidates:
        try:
            subprocess.Popen(
                [cmd, directory],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except (FileNotFoundError, PermissionError):
            continue
    return False


def fmt_time(seconds):
    if not seconds:
        return '0m'
    h, rem = divmod(int(seconds), 3600)
    m = rem // 60
    if h:
        return f'{h}h {m}m' if m else f'{h}h'
    return f'{m}m'
