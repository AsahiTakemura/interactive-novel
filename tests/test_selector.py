import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SELECTOR = ROOT / 'skills' / 'interactive-novel' / 'scripts' / 'selector.py'


class SelectorTests(unittest.TestCase):
    def module(self):
        if not SELECTOR.exists():
            self.fail('The keyboard selector has not been implemented.')
        spec = importlib.util.spec_from_file_location('novel_selector', SELECTOR)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_down_and_enter_confirm_next_option(self):
        module = self.module()
        keys = iter(['down', 'enter'])
        self.assertEqual(module.choose(['主角', '配角', '讨论'], keys.__next__, io.StringIO(), '选择角色'), 1)

    def test_up_wraps_to_last_option(self):
        module = self.module()
        keys = iter(['up', 'enter'])
        self.assertEqual(module.choose(['主角', '配角', '讨论'], keys.__next__, io.StringIO(), '选择角色'), 2)

    def test_escape_cancels_without_selecting(self):
        module = self.module()
        self.assertIsNone(module.choose(['主角', '配角'], lambda: 'escape', io.StringIO(), '选择角色'))

    def test_pipe_fallback_returns_stable_id_and_writes_utf8_result(self):
        self.module()
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            options = Path(folder) / 'options.json'
            result = Path(folder) / 'result.json'
            options.write_text(json.dumps([{'id': 'main', 'label': '主角'}, {'id': 'side', 'label': '配角'}], ensure_ascii=False), encoding='utf-8')
            run = subprocess.run([sys.executable, '-X', 'utf8', str(SELECTOR), '--options-file', str(options), '--output', str(result)], input='2\n', capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(result.read_text(encoding='utf-8')), {'index': 2, 'id': 'side', 'label': '配角'})

    def test_cancel_preserves_existing_result_file(self):
        self.module()
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            result = Path(folder) / 'result.json'
            original = '{"id":"keep"}\n'
            result.write_text(original, encoding='utf-8')
            run = subprocess.run([sys.executable, '-X', 'utf8', str(SELECTOR), '--output', str(result), '主角', '配角'], input='q\n', capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(run.returncode, 2, run.stderr)
            self.assertEqual(result.read_text(encoding='utf-8'), original)

    def test_duplicate_ids_are_rejected(self):
        module = self.module()
        with self.assertRaises(ValueError):
            module.normalize_options([{'id': 'same', 'label': 'A'}, {'id': 'same', 'label': 'B'}])


if __name__ == '__main__':
    unittest.main(verbosity=2)
