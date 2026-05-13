import os
import subprocess
import sys

_COMMANDS_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(_COMMANDS_DIR)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(_BASE_DIR, '.env'))
except ImportError:
    pass


def django_setup():
    if _BASE_DIR not in sys.path:
        sys.path.insert(0, _BASE_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "devtracker.settings")
    import django

    django.setup()


def open_pycharm(directory):
    candidates = ["charm", "pycharm", "pycharm-professional", "pycharm-community"]

    toolbox_scripts = os.path.expanduser("~/.local/share/JetBrains/Toolbox/scripts")
    if os.path.isdir(toolbox_scripts):
        for name in sorted(os.listdir(toolbox_scripts)):
            if "pycharm" in name.lower():
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


def generate_session_summary(project_path, started_at, ended_at):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ℹ️   ANTHROPIC_API_KEY não definida — resumo pulado.")
        return None

    if not project_path or not os.path.isdir(project_path):
        print("ℹ️   Diretório do projeto não encontrado — resumo pulado.")
        return None

    try:
        check = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        if check.returncode != 0:
            print("ℹ️   Diretório não é um repositório git — resumo pulado.")
            return None
    except (FileNotFoundError, OSError):
        print("ℹ️   git não encontrado — resumo pulado.")
        return None

    from django.utils import timezone as tz
    after = tz.localtime(started_at).strftime("%Y-%m-%dT%H:%M:%S")
    before = tz.localtime(ended_at).strftime("%Y-%m-%dT%H:%M:%S")
    result = subprocess.run(
        ["git", "log", "--oneline", f"--after={after}", f"--before={before}"],
        cwd=project_path,
        capture_output=True,
        text=True,
    )
    commits = result.stdout.strip()
    if not commits:
        print("ℹ️   Nenhum commit no período — resumo pulado.")
        return None

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Resuma em 2-3 linhas em português o que foi feito nesta "
                        "sessão de desenvolvimento com base nos commits abaixo. "
                        "Seja objetivo e direto.\n\n" + commits
                    ),
                }
            ],
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"⚠️   Erro ao gerar resumo: {e}")
        return None


def fmt_time(seconds):
    if not seconds:
        return "0m"
    h, rem = divmod(int(seconds), 3600)
    m = rem // 60
    if h:
        return f"{h}h {m}m" if m else f"{h}h"
    return f"{m}m"
