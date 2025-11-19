import os
import re

# pages ディレクトリ
PAGES_DIR = "pages"

# 共通インポートブロック
COMMON_IMPORT = """from common.style import inject_css, card, endcard, bubble
from common.pathkit import data_dir, assets_dir
from common.fileio import read_json, write_json
from common.ai import ai_text, ai_json, ai_image
"""

def fix_file(path):
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    # --- 既存の src / utils 系インポートを削除 ---
    code = re.sub(r"from\s+src\.common\.[^\n]+\n", "", code)
    code = re.sub(r"from\s+src\.[^\n]+\n", "", code)
    code = re.sub(r"from\s+utils\.[^\n]+\n", "", code)

    # --- すでに共通インポートがある場合は追加しない ---
    if COMMON_IMPORT.strip() not in code:
        # 先頭の import streamlit の下に挿入する
        code = re.sub(
            r"(import streamlit as st[\s\S]*?\n)",
            r"\1" + COMMON_IMPORT + "\n",
            code,
            count=1
        )

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"修正完了: {path}")


def main():
    for file in os.listdir(PAGES_DIR):
        if file.endswith(".py"):
            fix_file(os.path.join(PAGES_DIR, file))


if __name__ == "__main__":
    main()
