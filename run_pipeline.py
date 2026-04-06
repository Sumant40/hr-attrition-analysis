import json
import os
import subprocess
import sys
from pathlib import Path

NOTEBOOKS = ['EDA.ipynb', 'preprocessing.ipynb', 'modelling.ipynb']
ROOT = Path(__file__).resolve().parent
SUPPORT_DIR = ROOT / 'outputs' / '.pipeline_jupyter'
KERNEL_NAME = 'hr-analysis-pipeline'


def detect_python_executable() -> Path:
    if os.name == 'nt':
        candidate = ROOT / '.venv' / 'Scripts' / 'python.exe'
    else:
        candidate = ROOT / '.venv' / 'bin' / 'python'

    if candidate.exists():
        return candidate
    return Path(sys.executable)


PYTHON_EXE = detect_python_executable()


def ensure_kernel_spec() -> str:
    kernel_dir = SUPPORT_DIR / 'kernels' / KERNEL_NAME
    kernel_dir.mkdir(parents=True, exist_ok=True)

    kernel_spec = {
        'argv': [str(PYTHON_EXE), '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
        'display_name': f'Pipeline ({PYTHON_EXE.name})',
        'language': 'python',
    }
    (kernel_dir / 'kernel.json').write_text(
        json.dumps(kernel_spec, indent=2),
        encoding='utf-8',
    )
    return KERNEL_NAME


def build_jupyter_env() -> dict[str, str]:
    config_dir = SUPPORT_DIR / 'config'
    data_dir = SUPPORT_DIR / 'data'
    runtime_dir = SUPPORT_DIR / 'runtime'
    ipython_dir = SUPPORT_DIR / 'ipython'
    config_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    ipython_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env['JUPYTER_CONFIG_DIR'] = str(config_dir)
    env['JUPYTER_DATA_DIR'] = str(data_dir)
    env['JUPYTER_PATH'] = str(SUPPORT_DIR)
    env['JUPYTER_RUNTIME_DIR'] = str(runtime_dir)
    env['IPYTHONDIR'] = str(ipython_dir)

    if os.name == 'nt':
        env.setdefault('JUPYTER_ALLOW_INSECURE_WRITES', 'true')

    return env


def run_notebook(path: str, *, env: dict[str, str], kernel_name: str) -> None:
    cmd = [
        str(PYTHON_EXE),
        '-m',
        'jupyter',
        'nbconvert',
        '--to',
        'notebook',
        '--execute',
        '--inplace',
        f'--ExecutePreprocessor.kernel_name={kernel_name}',
        path,
    ]
    subprocess.run(cmd, check=True, cwd=ROOT, env=env)


if __name__ == '__main__':
    kernel_name = ensure_kernel_spec()
    env = build_jupyter_env()

    print(f'Using Python interpreter: {PYTHON_EXE}')
    for notebook in NOTEBOOKS:
        print(f'Running {notebook}...')
        run_notebook(notebook, env=env, kernel_name=kernel_name)
    print('Pipeline completed successfully.')
