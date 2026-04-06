import subprocess
import sys

NOTEBOOKS = ['EDA.ipynb', 'preprocessing.ipynb', 'modelling.ipynb']


def run_notebook(path: str) -> None:
    cmd = [
        sys.executable,
        '-m',
        'jupyter',
        'nbconvert',
        '--to',
        'notebook',
        '--execute',
        '--inplace',
        path,
    ]
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    for notebook in NOTEBOOKS:
        print(f'Running {notebook}...')
        run_notebook(notebook)
    print('Pipeline completed successfully.')
