import { existsSync, readFileSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';

const root = fileURLToPath(new URL('../../', import.meta.url));
const local = join(root, 'var/local/dev/runner.json');
const saved = existsSync(local) ? JSON.parse(readFileSync(local, 'utf8')) : {};
const venv = join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const active = process.env.VIRTUAL_ENV && join(process.env.VIRTUAL_ENV, process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');
const python = process.env.MATHSTART_PYTHON || (existsSync(venv) ? venv : active || saved.python || 'python');
const child = spawn(python, [join(root, 'scripts/dev_server.py'), ...process.argv.slice(2)], { cwd: root, stdio: 'inherit', windowsHide: true, env: { ...process.env, PYTHONUTF8: '1' } });
child.on('error', () => { console.error('Не удалось запустить Python. Активируйте target venv или задайте MATHSTART_PYTHON.'); process.exitCode = 1; });
child.on('exit', code => { process.exitCode = code ?? 1; });
