import importlib.util
import os
import sys
from contextlib import contextmanager
from datetime import timedelta
from importlib.machinery import SourceFileLoader
from io import StringIO
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from tracker.models import Event, Project, Session

COMMANDS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'commands',
)

if COMMANDS_DIR not in sys.path:
    sys.path.insert(0, COMMANDS_DIR)


def load_command(name):
    path = os.path.join(COMMANDS_DIR, name)
    mod_name = name.replace('-', '_')
    loader = SourceFileLoader(mod_name, path)
    spec = importlib.util.spec_from_file_location(mod_name, path, loader=loader)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Carregado uma vez — django.setup() é idempotente
cmd_new_project  = load_command('new-project')
cmd_start_session = load_command('start-session')
cmd_end_session  = load_command('end-session')
cmd_reset_data   = load_command('reset-data')


@contextmanager
def captured_output():
    buf = StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        yield buf
    finally:
        sys.stdout = old


# ─── helpers ───────────────────────────────────────────────

def make_project(**kwargs):
    defaults = {'name': 'Test', 'slug': 'test', 'nickname': 'test', 'path': '/tmp'}
    defaults.update(kwargs)
    return Project.objects.create(**defaults)


def make_session(project, started_at=None, ended_at=None):
    return Session.objects.create(
        project=project,
        started_at=started_at or timezone.now(),
        ended_at=ended_at,
    )


# ═══════════════════════════════════════════════════════════
# new-project
# ═══════════════════════════════════════════════════════════

class TestNewProject(TestCase):

    @patch('subprocess.Popen')
    def test_cria_com_todos_os_parametros(self, _):
        with patch('sys.argv', ['new-project', '--name', 'Meu App', '--nickname', 'meuapp', '--dir', '/tmp']):
            with captured_output():
                cmd_new_project.main()
        proj = Project.objects.get(nickname='meuapp')
        self.assertEqual(proj.name, 'Meu App')
        self.assertEqual(proj.path, '/tmp')

    @patch('subprocess.Popen')
    def test_nickname_derivado_do_nome_quando_omitido(self, _):
        with patch('sys.argv', ['new-project', '--name', 'Meu Projeto']):
            with captured_output():
                cmd_new_project.main()
        self.assertTrue(Project.objects.filter(nickname='meu-projeto').exists())

    @patch('subprocess.Popen')
    def test_diretorio_atual_quando_dir_omitido(self, _):
        with patch('sys.argv', ['new-project', '--name', 'App', '--nickname', 'app']):
            with captured_output():
                cmd_new_project.main()
        self.assertEqual(Project.objects.get(nickname='app').path, os.getcwd())

    def test_nickname_duplicado_retorna_erro(self):
        make_project(name='Existente', slug='existente', nickname='meuapp')
        with patch('sys.argv', ['new-project', '--name', 'Outro', '--nickname', 'meuapp']):
            with captured_output():
                with self.assertRaises(SystemExit) as cm:
                    cmd_new_project.main()
        self.assertEqual(cm.exception.code, 1)
        self.assertEqual(Project.objects.filter(nickname='meuapp').count(), 1)

    def test_nickname_com_espaco_retorna_erro(self):
        with patch('sys.argv', ['new-project', '--name', 'App', '--nickname', 'nick invalido']):
            with captured_output():
                with self.assertRaises(SystemExit) as cm:
                    cmd_new_project.main()
        self.assertEqual(cm.exception.code, 1)
        self.assertFalse(Project.objects.exists())

    def test_nickname_com_caractere_especial_retorna_erro(self):
        with patch('sys.argv', ['new-project', '--name', 'App', '--nickname', 'nick@app']):
            with captured_output():
                with self.assertRaises(SystemExit) as cm:
                    cmd_new_project.main()
        self.assertEqual(cm.exception.code, 1)

    @patch('subprocess.Popen')
    def test_modo_interativo_com_todos_os_defaults(self, _):
        # name digitado, apelido e dir confirmados com Enter
        with patch('sys.argv', ['new-project']):
            with patch('builtins.input', side_effect=['Projeto Interativo', '', '']):
                with captured_output():
                    cmd_new_project.main()
        self.assertTrue(Project.objects.filter(nickname='projeto-interativo').exists())

    @patch('subprocess.Popen')
    def test_modo_interativo_com_nickname_customizado(self, _):
        with patch('sys.argv', ['new-project']):
            with patch('builtins.input', side_effect=['Meu Projeto', 'meuprojeto', '/tmp']):
                with captured_output():
                    cmd_new_project.main()
        self.assertTrue(Project.objects.filter(nickname='meuprojeto').exists())

    def test_modo_interativo_nome_vazio_retorna_erro(self):
        with patch('sys.argv', ['new-project']):
            with patch('builtins.input', side_effect=['']):
                with captured_output():
                    with self.assertRaises(SystemExit) as cm:
                        cmd_new_project.main()
        self.assertEqual(cm.exception.code, 1)
        self.assertFalse(Project.objects.exists())

    @patch('subprocess.Popen')
    def test_pycharm_e_aberto_apos_criacao(self, mock_popen):
        with patch('sys.argv', ['new-project', '--name', 'App', '--nickname', 'app', '--dir', '/tmp']):
            with captured_output():
                cmd_new_project.main()
        mock_popen.assert_called_once()


# ═══════════════════════════════════════════════════════════
# start-session
# ═══════════════════════════════════════════════════════════

class TestStartSession(TestCase):

    @patch('subprocess.Popen')
    def test_cria_sessao_para_projeto_valido(self, _):
        make_project(nickname='myapp')
        with patch('sys.argv', ['start-session', 'myapp']):
            with captured_output():
                cmd_start_session.main()
        self.assertEqual(Session.objects.filter(project__nickname='myapp', ended_at__isnull=True).count(), 1)

    @patch('subprocess.Popen')
    def test_cria_evento_session_start(self, _):
        make_project(nickname='myapp')
        with patch('sys.argv', ['start-session', 'myapp']):
            with captured_output():
                cmd_start_session.main()
        self.assertTrue(Event.objects.filter(event_type='session_start').exists())

    def test_apelido_inexistente_retorna_erro(self):
        with patch('sys.argv', ['start-session', 'naoexiste']):
            with captured_output():
                with self.assertRaises(SystemExit) as cm:
                    cmd_start_session.main()
        self.assertEqual(cm.exception.code, 1)

    @patch('subprocess.Popen')
    def test_auto_fecha_sessao_do_mesmo_dia_no_now(self, _):
        project = make_project(nickname='myapp')
        before = timezone.now()
        sessao_aberta = make_session(project)

        with patch('sys.argv', ['start-session', 'myapp']):
            with captured_output():
                cmd_start_session.main()

        sessao_aberta.refresh_from_db()
        after = timezone.now()
        self.assertTrue(sessao_aberta.auto_closed)
        self.assertGreaterEqual(sessao_aberta.ended_at, before)
        self.assertLessEqual(sessao_aberta.ended_at, after)

    @patch('subprocess.Popen')
    def test_auto_fecha_sessao_de_dia_anterior_as_2359(self, _):
        project = make_project(nickname='myapp')
        ontem = timezone.now() - timedelta(days=1)
        sessao_aberta = make_session(project, started_at=ontem)

        with patch('sys.argv', ['start-session', 'myapp']):
            with captured_output():
                cmd_start_session.main()

        sessao_aberta.refresh_from_db()
        self.assertTrue(sessao_aberta.auto_closed)
        encerrado = timezone.localtime(sessao_aberta.ended_at)
        self.assertEqual(encerrado.hour, 23)
        self.assertEqual(encerrado.minute, 59)
        self.assertEqual(encerrado.date(), timezone.localtime(ontem).date())

    @patch('subprocess.Popen')
    def test_nova_sessao_criada_apos_auto_fechamento(self, _):
        project = make_project(nickname='myapp')
        make_session(project)

        with patch('sys.argv', ['start-session', 'myapp']):
            with captured_output():
                cmd_start_session.main()

        self.assertEqual(Session.objects.filter(project=project).count(), 2)
        self.assertEqual(Session.objects.filter(project=project, ended_at__isnull=True).count(), 1)

    @patch('subprocess.Popen')
    def test_pycharm_aberto_quando_diretorio_existe(self, mock_popen):
        make_project(nickname='myapp', path='/tmp')
        with patch('sys.argv', ['start-session', 'myapp']):
            with captured_output():
                cmd_start_session.main()
        mock_popen.assert_called_once()

    @patch('subprocess.Popen')
    def test_pycharm_nao_aberto_quando_diretorio_inexistente(self, mock_popen):
        make_project(nickname='myapp', path='/tmp/pasta-que-nao-existe-xyz')
        with patch('sys.argv', ['start-session', 'myapp']):
            with captured_output():
                cmd_start_session.main()
        mock_popen.assert_not_called()


# ═══════════════════════════════════════════════════════════
# end-session
# ═══════════════════════════════════════════════════════════

class TestEndSession(TestCase):

    def test_sem_sessao_ativa_exibe_info_e_sai_com_zero(self):
        with patch('sys.argv', ['end-session']):
            with captured_output() as out:
                cmd_end_session.main()   # não deve levantar SystemExit
        self.assertIn('Nenhuma sessão ativa', out.getvalue())

    def test_encerra_sessao_ativa_sem_nickname(self):
        project = make_project(nickname='myapp')
        make_session(project)
        with patch('sys.argv', ['end-session']):
            with captured_output():
                cmd_end_session.main()
        self.assertFalse(Session.objects.filter(project__nickname='myapp', ended_at__isnull=True).exists())

    def test_encerra_sessao_ativa_com_nickname_correto(self):
        project = make_project(nickname='myapp')
        make_session(project)
        with patch('sys.argv', ['end-session', 'myapp']):
            with captured_output():
                cmd_end_session.main()
        self.assertFalse(Session.objects.filter(project__nickname='myapp', ended_at__isnull=True).exists())

    def test_nickname_errado_retorna_erro_sem_fechar(self):
        project = make_project(nickname='myapp')
        make_session(project)
        with patch('sys.argv', ['end-session', 'outro']):
            with captured_output():
                with self.assertRaises(SystemExit) as cm:
                    cmd_end_session.main()
        self.assertEqual(cm.exception.code, 1)
        self.assertTrue(Session.objects.filter(project__nickname='myapp', ended_at__isnull=True).exists())

    def test_cria_evento_session_end(self):
        project = make_project(nickname='myapp')
        make_session(project)
        with patch('sys.argv', ['end-session']):
            with captured_output():
                cmd_end_session.main()
        self.assertTrue(Event.objects.filter(event_type='session_end').exists())

    def test_salva_notes_quando_fornecidas(self):
        project = make_project(nickname='myapp')
        make_session(project)
        with patch('sys.argv', ['end-session', '--notes', 'implementei login']):
            with captured_output():
                cmd_end_session.main()
        self.assertEqual(Session.objects.get(project__nickname='myapp').notes, 'implementei login')

    def test_exibe_resumo_com_horario(self):
        project = make_project(nickname='myapp')
        make_session(project)
        with patch('sys.argv', ['end-session']):
            with captured_output() as out:
                cmd_end_session.main()
        output = out.getvalue()
        self.assertIn('Sessão encerrada', output)
        self.assertIn('Horário', output)
        self.assertIn('Total acum.', output)


# ═══════════════════════════════════════════════════════════
# reset-data
# ═══════════════════════════════════════════════════════════

class TestResetData(TestCase):

    def _popular(self):
        p1 = make_project(name='Proj 1', slug='proj-1', nickname='proj1', path='/tmp')
        p2 = make_project(name='Proj 2', slug='proj-2', nickname='proj2', path='/tmp')
        make_session(p1)
        make_session(p2)
        return p1, p2

    def test_apaga_projeto_especifico_com_flag_y(self):
        self._popular()
        with patch('sys.argv', ['reset-data', '--nickname', 'proj1', '-y']):
            with captured_output():
                cmd_reset_data.main()
        self.assertFalse(Project.objects.filter(nickname='proj1').exists())
        self.assertTrue(Project.objects.filter(nickname='proj2').exists())

    def test_apaga_projeto_especifico_confirmado_com_s(self):
        self._popular()
        with patch('sys.argv', ['reset-data', '--nickname', 'proj1']):
            with patch('builtins.input', return_value='s'):
                with captured_output():
                    cmd_reset_data.main()
        self.assertFalse(Project.objects.filter(nickname='proj1').exists())

    def test_cancela_quando_resposta_e_n(self):
        self._popular()
        with patch('sys.argv', ['reset-data', '--nickname', 'proj1']):
            with patch('builtins.input', return_value='n'):
                with captured_output():
                    cmd_reset_data.main()
        self.assertTrue(Project.objects.filter(nickname='proj1').exists())

    def test_nickname_inexistente_retorna_erro(self):
        with patch('sys.argv', ['reset-data', '--nickname', 'naoexiste']):
            with captured_output():
                with self.assertRaises(SystemExit) as cm:
                    cmd_reset_data.main()
        self.assertEqual(cm.exception.code, 1)

    def test_apaga_tudo_com_flag_y(self):
        self._popular()
        with patch('sys.argv', ['reset-data', '-y']):
            with captured_output():
                cmd_reset_data.main()
        self.assertEqual(Project.objects.count(), 0)
        self.assertEqual(Session.objects.count(), 0)
        self.assertEqual(Event.objects.count(), 0)

    def test_apaga_tudo_confirmado_com_s(self):
        self._popular()
        with patch('sys.argv', ['reset-data']):
            with patch('builtins.input', return_value='s'):
                with captured_output():
                    cmd_reset_data.main()
        self.assertEqual(Project.objects.count(), 0)

    def test_cancela_reset_total_quando_resposta_e_n(self):
        self._popular()
        with patch('sys.argv', ['reset-data']):
            with patch('builtins.input', return_value='n'):
                with captured_output():
                    cmd_reset_data.main()
        self.assertEqual(Project.objects.count(), 2)

    def test_sessoes_em_cascata_ao_apagar_projeto(self):
        self._popular()
        with patch('sys.argv', ['reset-data', '--nickname', 'proj1', '-y']):
            with captured_output():
                cmd_reset_data.main()
        self.assertFalse(Session.objects.filter(project__nickname='proj1').exists())
        self.assertEqual(Session.objects.count(), 1)   # sessão do proj2 permanece
