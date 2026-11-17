import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('setup_tool', str(ROOT / 'omarchy-logitech-ergo'))
spec = importlib.util.spec_from_loader(loader.name, loader)
tool = importlib.util.module_from_spec(spec)
loader.exec_module(tool)


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        (self.home / 'hypr').mkdir()
        self.bindings = self.home / 'hypr/bindings.lua'
        self.module = self.home / 'hypr/logitech-ergo.lua'
        self.original = '-- Personal settings\no.bind("SUPER + B", "Browser", "chromium")\n'
        self.bindings.write_text(self.original)

    def install(self):
        tool.apply('install', self.home, no_reload=True)

    def test_install_idempotent_preserves_personal_bindings(self):
        self.install()
        first = self.bindings.read_text()
        self.install()
        self.assertEqual(first, self.bindings.read_text())
        self.assertTrue(first.startswith(self.original))
        self.assertEqual(first.count(tool.START), 1)
        self.assertEqual(self.module.read_text(), tool.MODULE)

    def test_uninstall_preserves_later_edits(self):
        self.install()
        with self.bindings.open('a') as file:
            file.write('-- Added later\n')
        tool.apply('uninstall', self.home, no_reload=True)
        self.assertNotIn(tool.START, self.bindings.read_text())
        self.assertIn('-- Added later', self.bindings.read_text())
        self.assertIn(self.original, self.bindings.read_text())
        self.assertFalse(self.module.exists())
        tool.apply('uninstall', self.home, no_reload=True)

    def test_backup_contains_original(self):
        self.install()
        backups = list((self.home / 'omarchy-logitech-ergo/backups').glob('*/bindings.lua'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), self.original)

    def test_custom_module_refused(self):
        self.module.write_text('-- mine\n')
        with self.assertRaises(tool.SetupError):
            self.install()
        self.assertEqual(self.bindings.read_text(), self.original)
        self.assertEqual(self.module.read_text(), '-- mine\n')

    def test_malformed_marker_refused(self):
        self.bindings.write_text(self.original + tool.START + '\n')
        with self.assertRaises(tool.SetupError):
            self.install()

    def test_symlink_refused(self):
        self.bindings.rename(self.home / 'original.lua')
        self.bindings.symlink_to(self.home / 'original.lua')
        with self.assertRaises(tool.SetupError):
            self.install()

    def test_install_rolls_back_on_validation_failure(self):
        with patch.object(tool, 'run', return_value=''), patch.object(
            tool, 'reload_config', side_effect=[tool.SetupError('invalid'), None]
        ) as reload:
            with self.assertRaises(tool.SetupError):
                tool.apply('install', self.home)
        self.assertEqual(reload.call_count, 2)
        self.assertEqual(self.bindings.read_text(), self.original)
        self.assertFalse(self.module.exists())

    def test_uninstall_rolls_back_on_validation_failure(self):
        self.install()
        installed = self.bindings.read_text()
        with patch.object(tool, 'run', return_value=''), patch.object(
            tool, 'reload_config', side_effect=[tool.SetupError('invalid'), None]
        ):
            with self.assertRaises(tool.SetupError):
                tool.apply('uninstall', self.home)
        self.assertEqual(self.bindings.read_text(), installed)
        self.assertEqual(self.module.read_text(), tool.MODULE)

    def test_existing_errors_refused_before_write(self):
        with patch.object(tool, 'run', return_value='existing error'):
            with self.assertRaises(tool.SetupError):
                tool.apply('install', self.home)
        self.assertEqual(self.bindings.read_text(), self.original)
        self.assertFalse(self.module.exists())

    def test_keyboard_configuration_uses_requested_device(self):
        with patch.object(tool, 'run', return_value='ok') as run:
            tool.configure_keyboard('my-device')
        self.assertEqual(run.call_args_list[0].args[0],
                         ['solaar', 'config', 'my-device', 'multiplatform', 'Windows'])
        self.assertEqual(run.call_args_list[1].args[0],
                         ['solaar', 'config', 'my-device', 'fn-swap', 'on'])


if __name__ == '__main__':
    unittest.main()
