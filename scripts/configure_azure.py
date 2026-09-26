"""Prompt for an Azure key locally without echoing it or putting it in shell history."""
from getpass import getpass
from pathlib import Path
import os
import re
import subprocess
import tempfile


def main():
    root = Path(__file__).resolve().parents[1]
    path = root / '.env'
    if subprocess.run(['git', 'check-ignore', '-q', '.env'], cwd=root).returncode:
        raise SystemExit('Refusing to write credentials: .env is not ignored by Git.')
    if subprocess.run(['git', 'ls-files', '--error-unmatch', '.env'], cwd=root,
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        raise SystemExit('Refusing to write credentials: .env is tracked by Git.')
    key = getpass('Azure OpenAI API key (hidden input): ').strip()
    if not key or any(c in key for c in '\r\n\"\''):
        raise SystemExit('No valid key entered; .env unchanged.')
    text = path.read_text() if path.exists() else ''
    line = 'AZURE_OPENAI_API_KEY=' + key
    if re.search(r'^AZURE_OPENAI_API_KEY=.*$', text, re.M):
        text = re.sub(r'^AZURE_OPENAI_API_KEY=.*$', lambda _: line, text, flags=re.M)
    else:
        text = text.rstrip('\n') + '\n' + line + '\n'
    fd, temporary = tempfile.mkstemp(prefix='.env.', dir=root)
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)
    print('Saved the key to the ignored .env with owner-only permissions. Key not displayed.')


if __name__ == '__main__':
    main()
