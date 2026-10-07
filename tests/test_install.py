import importlib.util
from pathlib import Path
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def module(self):
        spec = importlib.util.spec_from_file_location('bundle_installer', PACKAGE / 'install.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_fresh_install_discovers_both_skills(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.module().install(root / '.codex', root / '.agents')
            for name in ('yoshino-tone', 'interactive-novel'):
                self.assertTrue((root / '.codex' / 'skills' / name / 'SKILL.md').is_file())
            self.assertTrue((root / '.codex' / 'skills' / 'interactive-novel' / 'scripts' / 'selector.py').is_file())

    def test_existing_agents_novel_is_updated_in_place_with_backup(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            novel = root / '.agents' / 'skills' / 'interactive-novel'
            novel.mkdir(parents=True)
            (novel / 'SKILL.md').write_text('old version', encoding='utf-8')
            (novel / 'progress.json').write_text('{"chapter":4}', encoding='utf-8')
            self.module().install(root / '.codex', root / '.agents')
            self.assertEqual((novel / 'SKILL.md').read_bytes(), (PACKAGE / 'skills' / 'interactive-novel' / 'SKILL.md').read_bytes())
            self.assertEqual((novel / 'progress.json').read_text(encoding='utf-8'), '{"chapter":4}')
            self.assertFalse((root / '.codex' / 'skills' / 'interactive-novel').exists())
            backups = list((root / '.codex' / 'backups').glob('interactive-novel-*'))
            self.assertEqual(len(backups), 1)
            self.assertEqual((backups[0] / 'SKILL.md').read_text(encoding='utf-8'), 'old version')

    def test_existing_memory_and_agents_are_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            codex = root / '.codex'
            memory = codex / 'skills' / 'yoshino-tone' / 'memory'
            memory.mkdir(parents=True)
            (memory / 'profile.md').write_text('remember my preference', encoding='utf-8')
            (codex / 'AGENTS.md').write_text('personal rules', encoding='utf-8')
            installer = self.module()
            installer.install(codex, root / '.agents')
            self.assertEqual((memory / 'profile.md').read_text(encoding='utf-8'), 'remember my preference')
            self.assertEqual((codex / 'AGENTS.md').read_text(encoding='utf-8'), 'personal rules')
            self.assertTrue((memory / 'fiction.md').is_file())
            count = len(list((codex / 'backups').iterdir()))
            installer.install(codex, root / '.agents')
            self.assertEqual(len(list((codex / 'backups').iterdir())), count)

    def test_dry_run_makes_no_directories(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.module().install(root / '.codex', root / '.agents', dry_run=True)
            self.assertEqual(list(root.iterdir()), [])

    def test_invalid_target_stops_before_installing_either_skill(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            bad = root / '.agents' / 'skills' / 'interactive-novel'
            bad.parent.mkdir(parents=True)
            bad.write_text('not a folder', encoding='utf-8')
            with self.assertRaises(ValueError):
                self.module().install(root / '.codex', root / '.agents')
            self.assertFalse((root / '.codex').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
