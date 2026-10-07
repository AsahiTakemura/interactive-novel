#!/usr/bin/env python3
"""Optional arrow-key selector. Standard library only; prints the confirmed choice as JSON."""
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unicodedata


def normalize_options(raw):
    if not isinstance(raw, list) or not raw:
        raise ValueError('Options must be a non-empty JSON array.')
    options, ids = [], set()
    for index, item in enumerate(raw, 1):
        if isinstance(item, str):
            option = {'id': str(index), 'label': item}
        elif isinstance(item, dict) and 'id' in item and 'label' in item:
            if not isinstance(item['id'], (str, int)) or isinstance(item['id'], bool):
                raise ValueError('Each option id must be a string or integer.')
            option = {'id': str(item['id']), 'label': item['label']}
        else:
            raise ValueError('Each option must be a label or an object with id and label.')
        if not option['id'] or option['id'] in ids:
            raise ValueError('Option ids must be non-empty and unique.')
        if not isinstance(option['label'], str) or not option['label'].strip():
            raise ValueError('Each option needs a non-empty text label.')
        ids.add(option['id'])
        options.append(option)
    return options


def clip(text, width):
    text = ''.join(' ' if unicodedata.category(char) == 'Cc' else char for char in str(text))
    result, used = [], 0
    for char in text:
        size = 0 if unicodedata.combining(char) else (2 if unicodedata.east_asian_width(char) in 'WF' else 1)
        if used + size > width - 1:
            return ''.join(result) + '…'
        result.append(char)
        used += size
    return ''.join(result)


def choose(labels, read_key, output, title):
    selected, previous_lines = 0, 0
    while True:
        if previous_lines:
            output.write(f'\x1b[{previous_lines}A')
        width = max(10, shutil.get_terminal_size((80, 24)).columns - 1)
        lines = [title, '↑/↓ 移动 · Enter 确认 · Esc 取消']
        lines += [('> ' if index == selected else '  ') + label for index, label in enumerate(labels)]
        for line in lines:
            output.write('\r\x1b[2K' + clip(line, width) + '\n')
        output.flush()
        previous_lines = len(lines)
        key = read_key()
        if key == 'up':
            selected = (selected - 1) % len(labels)
        elif key == 'down':
            selected = (selected + 1) % len(labels)
        elif key == 'enter':
            return selected
        elif key == 'escape':
            return None


@contextmanager
def keyboard_reader():
    if os.name == 'nt':
        import ctypes
        import msvcrt
        kernel = ctypes.windll.kernel32
        kernel.GetStdHandle.restype = ctypes.c_void_p
        handle = kernel.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        if not kernel.GetConsoleMode(ctypes.c_void_p(handle), ctypes.byref(mode)):
            raise OSError('An interactive console is required for arrow keys.')
        if not kernel.SetConsoleMode(ctypes.c_void_p(handle), mode.value | 4):
            raise OSError('This console does not support menu redraw.')

        def read_key():
            key = msvcrt.getwch()
            if key in ('\x00', '\xe0'):
                return {'H': 'up', 'P': 'down'}.get(msvcrt.getwch(), '')
            return {'\r': 'enter', '\x1b': 'escape', '\x03': 'escape'}.get(key, '')

        try:
            yield read_key
        finally:
            kernel.SetConsoleMode(ctypes.c_void_p(handle), mode.value)
    else:
        import select
        import termios
        import tty
        descriptor = sys.stdin.fileno()
        original = termios.tcgetattr(descriptor)
        tty.setcbreak(descriptor)

        def read_key():
            key = sys.stdin.read(1)
            if key == '\x1b':
                if select.select([sys.stdin], [], [], 0.05)[0]:
                    suffix = sys.stdin.read(2)
                    return {'[A': 'up', '[B': 'down'}.get(suffix, '')
                return 'escape'
            return {'\r': 'enter', '\n': 'enter', '\x03': 'escape'}.get(key, '')

        try:
            yield read_key
        finally:
            termios.tcsetattr(descriptor, termios.TCSADRAIN, original)


def numeric_choice(options, title):
    print(title)
    for index, option in enumerate(options, 1):
        print(f'[{index}] {option["label"]}')
    while True:
        try:
            answer = input('输入编号确认，或 q 取消: ').strip()
        except EOFError:
            return None
        if answer.lower() == 'q':
            return None
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return int(answer) - 1
        print('请输入有效编号。')


def save_result(path, result):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, prefix='.selection-', delete=False) as file:
        temporary = Path(file.name)
        json.dump(result, file, ensure_ascii=False)
        file.write('\n')
    try:
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('options', nargs='*', help='Labels, when no options file is supplied.')
    parser.add_argument('--title', default='请选择')
    parser.add_argument('--options-file', type=Path)
    parser.add_argument('--output', type=Path, help='Write JSON only after a confirmed selection.')
    args = parser.parse_args()
    try:
        if args.options_file and args.options:
            raise ValueError('Use either positional labels or --options-file, not both.')
        raw = json.loads(args.options_file.read_text(encoding='utf-8-sig')) if args.options_file else args.options
        options = normalize_options(raw)
        if sys.stdin.isatty() and sys.stdout.isatty():
            try:
                with keyboard_reader() as read_key:
                    index = choose([option['label'] for option in options], read_key, sys.stdout, args.title)
            except OSError:
                print('当前终端不支持方向键，改用编号选择。')
                index = numeric_choice(options, args.title)
        else:
            index = numeric_choice(options, args.title)
        if index is None:
            print('Selection canceled; no result was written.', file=sys.stderr)
            return 2
        result = {'index': index + 1, **options[index]}
        if args.output:
            save_result(args.output, result)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except KeyboardInterrupt:
        print('\nSelection canceled; no result was written.', file=sys.stderr)
        return 2
    except (OSError, ValueError) as error:
        print(f'Selector error: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
