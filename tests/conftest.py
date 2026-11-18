import pathlib
import sys

# Permite `import app` e `import config` ao rodar `pytest` na raiz do projeto
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
