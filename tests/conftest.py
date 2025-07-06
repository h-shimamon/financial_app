# tests/conftest.py

import os
import sys

# このファイル (tests/conftest.py) のひとつ上のディレクトリを
# sys.path に追加 → これで data.py, calculations.py がインポート可能に
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
