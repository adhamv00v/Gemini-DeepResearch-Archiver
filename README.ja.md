[English](README.md) | 日本語

# Gemini-DeepResearch-Archiver
Capture & Archive Google Gemini Deep Research as local Markdown (Obsidian-ready)

**Gemini-DeepResearch-Archiver** は、Google Gemini の **Deep Research（深層調査）レポートをローカルに完全保存するための OSS アーカイバ**です。

通常、Gemini の Deep Research は **DOM から取得できず、ブラウザ拡張では抽出不可能**ですが、本プロジェクトは **mitmproxy によるネットワーク層の解析**により、Deep Research の最終レポートを安定して抽出します。

さらに、Obsidian で使いやすいように **Markdown + YAML フロントマター形式**で保存し、**チャットセッションとの双方向リンク**まで自動生成します。

---

## 🚀 特徴（Features）

### ✔ Deep Research の「最終レポート」を完全抽出
- Gemini の batchexecute 通信から wrb.fr の JSON を解析
- 思考過程ではなく**最終レポート本文のみ**を抽出
- Markdown 内の H1 重複を防ぎ、Obsidian 表示を最適化

### ✔ Obsidian での閲覧に最適化
- YAML フロントマターを自動生成
- タイトル・日付・タグ・元チャットへのリンクを付与
- レポート本文は Markdown としてそのまま利用可能

### ✔ チャットノート & Deep Research の双方向リンク
- 1 セッションごとにチャットノートを自動生成
- Deep Research → チャット / チャット → Deep Research の**双方向内部リンク**を生成

### ✔ captured_data のログから一括処理（バッチ解析）
- mitmproxy が保存したログを一括解析
- ファイル名の衝突を回避
- 日付＋タイトルの整ったフォルダ構成で保存

---

## 📁 フォルダ構造（project structure）
```
Gemini-DeepResearch-Archiver/
├ addon_raw_logger.py        # mitmproxy用のRawログ取得アドオン
├ dr_chat_batch_parse.py     # Deep Research & Chatパーサ
│
├ captured_data/             # mitmproxyが生成したrawログ（入力）
├ dr_output/                 # Deep Research Markdown（出力）
├ chat_output/               # チャットノート（出力）
│
├ setup/
│ ├ setup_windows.bat        # 初期セットアップ
│ ├ start_capture.bat        # mitmproxy起動＋Gemini自動オープン
│ └ stop_capture.bat         # mitmproxy終了
│
├ docs/                      # 図解など（任意）
├ example/                   # 匿名化サンプルログ
│
├ LICENSE                    # MIT License
└ README.md                  # このファイル
```
---

## 🛠 インストール（Installation）

### 1. Python（3.9〜3.12推奨）をインストール
公式サイトから Python を入れてください。
### 2. 依存ライブラリのインストール
```
pip install mitmproxy
```
### 3. mitmproxy 証明書のインストール

初回のみ以下を実行：
```
mitmproxy
```
ブラウザで以下を開き、証明書を OS ＆ブラウザにインストールします：
```
http://mitm.it
```

---

## 🧪 使い方（Usage）

### Step 1：ログキャプチャ開始
```
mitmweb -s addon_raw_logger.py
```

または setup/start_capture.bat を実行 →  
- mitmproxy が起動
- Gemini が自動で開く

### Step 2：Gemini の Deep Research を実行
- Deep Research の開始
- 最終レポートが表示されるまで待つ  
- この間の通信が captured_data/ に保存される

### Step 3：ログの解析（Markdown生成）
```
python dr_chat_batch_parse.py
```
生成されるもの：

- dr_output/ … Deep Research 最終レポート（Markdown）
- chat_output/ … チャットセッションノート（Markdown）

### Step 4：Obsidian Vault に取り込む
dr_output/ と chat_output/ を Vault に追加するだけ。

---

## 📄 出力例（Deep Research ノート）
```
---
title: 3DCGから3Dプリント手順
date: 2025-11-30
tags: [DeepResearch, Gemini]
source_chat: [[2025-11-30_18-09-35_993_batchexecute-Session]]
---

# 3DCGから3Dプリント手順

## 1. モデリングデータの要件
（本文）

---

## 出典チャット
[[2025-11-30_18-09-35_993_batchexecute-Session]]
```
---

## 🔒 セキュリティ注意（IMPORTANT）

- 本ツールは HTTPS を MITM する仕組みのため、**mitmproxy の証明書をインストールすると「全HTTPS通信が復号可能」**になります。
- 必ず**信頼できるローカル環境**で使用してください。
- 公共Wi-Fi・共有端末では使用しないでください。
- 本ツールは**あなた自身の Gemini アカウントに対してのみ使用してください。**

---

## 📌 ロードマップ（Roadmap）

- [ ] **Level 3 完全自動化**（Chrome Extension + Local Server + mitmproxy）
- [ ] Chat本文の自動抽出
- [ ] RAG用 JSON/chunk 形式出力
- [ ] Obsidian 自動同期
- [ ] GitHub Actions の導入
- [ ] PyPI パッケージ化

---

## 🤝 コントリビューション（Contributing）

Issue / Pull Request 大歓迎！  
改善点の提案、バグ報告、PRなどお待ちしています。

---

## 📄 ライセンス（License）

本プロジェクトは **MIT License** のもと提供されます。  
詳細は `LICENSE` を参照してください。
