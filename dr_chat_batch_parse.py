#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gemini Deep Research + Chat ノート自動生成スクリプト（Obsidian向け）

機能:
- captured_data/ 以下の *_batchexecute.txt をすべて走査
- wrb.fr を含むものから Deep Research 最終レポートを抽出
- Deep Research ノート: dr_output/ に自動保存
  - YAML frontmatter（双方向リンク含む）
  - 本文：H1見出しを自動削除（重複防止）
- チャットノート: chat_output/ に自動保存
  - Deep Research ノートへの内部リンク付き

"""

import os
import sys
import glob
import json
from datetime import datetime
from typing import Any, List, Dict


# ============================================================
# 共通ユーティリティ
# ============================================================

def safe_title(text: str) -> str:
    """ファイル名として安全な文字列にする"""
    invalid = r'\\/:*?"<>|'
    for ch in invalid:
        text = text.replace(ch, "_")
    return text.strip()


def get_date_from_basename(basename: str) -> str:
    """ファイル名の先頭 YYYY-MM-DD を抽出する"""
    return basename.split("_")[0]


def safe_print(msg: str) -> None:
    """Windows 環境でも安全に print"""
    try:
        print(msg)
    except UnicodeEncodeError:
        try:
            print(msg.encode("cp932", errors="replace").decode("cp932"))
        except Exception:
            pass


# ============================================================
# Deep Research 本文から H1 行を取り除く
# ============================================================

def strip_leading_h1(markdown_text: str) -> str:
    """
    Deep Research 最終レポート本文の先頭 H1（# タイトル）を取り除く。
    """
    lines = markdown_text.splitlines()
    if lines and lines[0].strip().startswith("# "):
        return "\n".join(lines[1:]).lstrip()
    return markdown_text


# ============================================================
# 1. wrb.fr 文字列抽出
# ============================================================

def parse_batchexecute_file(path: str) -> List[str]:
    """ wrb.fr の第3要素（巨大JSON文字列）を抽出 """
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()

    lines = txt.splitlines()

    try:
        idx = lines.index("### RESPONSE BODY (raw)")
    except ValueError:
        return []

    i = idx + 1

    # 空行・XSSI ヘッダをスキップ
    while i < len(lines) and (not lines[i].strip() or lines[i].startswith(")]}'")):
        i += 1

    blobs = []

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # 長さ → JSON
        if line.isdigit():
            if i + 1 >= len(lines):
                break
            json_line = lines[i + 1]

            try:
                outer = json.loads(json_line)
            except Exception:
                outer = None

            if isinstance(outer, list):
                for row in outer:
                    if (
                        isinstance(row, list)
                        and len(row) >= 3
                        and row[0] == "wrb.fr"
                        and isinstance(row[2], str)
                    ):
                        blobs.append(row[2])

            i += 2
        else:
            # 長さなし JSON 保険
            try:
                outer = json.loads(line)
            except Exception:
                outer = None

            if isinstance(outer, list):
                for row in outer:
                    if (
                        isinstance(row, list)
                        and len(row) >= 3
                        and row[0] == "wrb.fr"
                        and isinstance(row[2], str)
                    ):
                        blobs.append(row[2])

            i += 1

    return blobs


# ============================================================
# 2. Deep Research 最終レポート抽出
# ============================================================

def extract_final_report(root: Any) -> List[str]:
    """
    最終レポート（Markdown）を抽出する。
    条件：
        - リスト
        - 長さ >= 5
        - obj[4] が文字列＆ '#' で始まる（Markdown H1）
    """
    results = []

    def rec(obj: Any) -> None:
        if isinstance(obj, list):
            if (
                len(obj) >= 5
                and isinstance(obj[4], str)
                and obj[4].lstrip().startswith("#")
            ):
                results.append(obj[4])
            for v in obj:
                rec(v)
        elif isinstance(obj, dict):
            for v in obj.values():
                rec(v)

    rec(root)
    return results


# ============================================================
# 3. Deep Research ノート出力
# ============================================================

def write_dr_markdown(date_str: str, title: str, body: str,
                      source_chat: str, out_dir: str,
                      existing_names: Dict[str, int]) -> str:
    """
    Deep Research ノートを書き出す。
    戻り値：作成したノート名（拡張子なし）
    """

    os.makedirs(out_dir, exist_ok=True)

    base = f"{date_str}-{safe_title(title)}"
    if base in existing_names:
        existing_names[base] += 1
        name = f"{base}_{existing_names[base]}"
    else:
        existing_names[base] = 1
        name = base

    out_path = os.path.join(out_dir, name + ".md")

    clean_body = strip_leading_h1(body)  # H1除去済み本文

    md = []
    md.append("---")
    md.append(f"title: {title}")
    md.append(f"date: {date_str}")
    md.append("tags: [DeepResearch, Gemini]")
    md.append(f"source_chat: [[{source_chat}]]")
    md.append("---")
    md.append("")
    md.append(f"# {title}")
    md.append("")
    md.append(clean_body)
    md.append("")
    md.append("---")
    md.append("## 出典チャット")
    md.append(f"[[{source_chat}]]")
    md.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    safe_print(f"  DRノート生成: {out_path}")

    return name


# ============================================================
# 4. チャットノート出力
# ============================================================

def write_chat_markdown(date_str: str, name: str,
                        dr_notes: List[str], out_dir: str) -> None:
    """チャットノートを書き出す"""

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, name + ".md")

    md = []
    md.append("---")
    md.append(f"title: Gemini Chat ({date_str})")
    md.append(f"date: {date_str}")
    md.append("tags: [GeminiChat]")
    md.append("---")
    md.append("")
    md.append(f"# Gemini Chat Log ({date_str})")
    md.append("")
    md.append("（チャット本文は未抽出。Deep Research リンクのみ含まれます。）")
    md.append("")
    md.append("---")
    md.append("## Deep Research Links")
    md.append("")

    for n in dr_notes:
        md.append(f"- [[{n}]]")

    md.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    safe_print(f"  チャットノート生成: {out_path}")


# ============================================================
# 5. メイン処理
# ============================================================

def main():
    in_dir = "captured_data"
    dr_dir = "dr_output"
    chat_dir = "chat_output"

    files = sorted(glob.glob(os.path.join(in_dir, "*_batchexecute.txt")))
    if not files:
        safe_print("batchexecute ファイルが見つかりません。")
        return

    safe_print(f"処理対象ファイル数: {len(files)}")

    dr_name_counter = {}

    for path in files:
        base = os.path.basename(path)
        date_str = get_date_from_basename(base)
        session_name = base.replace("_batchexecute.txt", "") + "-Session"

        safe_print(f"\n=== 処理中: {base} ===")

        blobs = parse_batchexecute_file(path)
        if not blobs:
            safe_print("  wrb.frなし → スキップ")
            continue

        dr_notes_for_session = []

        for i, blob in enumerate(blobs):
            safe_print(f"  wrb.fr #{i+1}")

            try:
                root = json.loads(blob)
            except Exception as e:
                safe_print(f"    JSONデコード失敗: {e}")
                continue

            finals = extract_final_report(root)
            if not finals:
                safe_print("    最終レポートなし → スキップ")
                continue

            report = finals[0]

            first = report.splitlines()[0].strip()
            if first.startswith("#"):
                title = first.lstrip("#").strip()
            else:
                title = "DeepResearch"

            note = write_dr_markdown(
                date_str=date_str,
                title=title,
                body=report,
                source_chat=session_name,
                out_dir=dr_dir,
                existing_names=dr_name_counter
            )
            dr_notes_for_session.append(note)

        if dr_notes_for_session:
            write_chat_markdown(
                date_str=date_str,
                name=session_name,
                dr_notes=dr_notes_for_session,
                out_dir=chat_dir
            )
        else:
            safe_print("  Deep Researchなし。チャットノート生成せず。")

    safe_print("\n◎ 全処理完了")


if __name__ == "__main__":
    main()
