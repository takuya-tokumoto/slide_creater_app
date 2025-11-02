# スライド作成アプリ

ES（自己PR等）を貼り付けて、AIでスライド構成案を生成し、チャットで編集してPPTXファイルとしてダウンロードできるWebアプリケーションです。

## 機能

- 📝 **ES入力**：複数セクション（タイトル＋本文）を追加/削除
- 🤖 **自動生成**：入力内容からスライド構成案を自動生成
- 💬 **チャット編集**：自然言語でスライドを編集
- 📊 **プレビュー**：リアルタイムでスライドを確認・編集
- 📥 **PPTX出力**：PowerPoint形式でダウンロード

## 技術スタック

- **バックエンド**：FastAPI (Python)
- **フロントエンド**：HTML + CSS + Vanilla JavaScript
- **PPTX生成**：python-pptx
- **AI生成**：Claude (Anthropic API)
- **実行環境**：ローカル環境（外部DB・クラウド不要）

## セットアップ

### 前提条件

- Python 3.8以上
- pip
- Anthropic API キー（AI機能を使用する場合）

### インストール

1. リポジトリをクローン（または作業ディレクトリに移動）

```bash
cd slide_creater_app
```

2. 仮想環境を作成してアクティベート（推奨）

```bash
# Windows (Git Bash)
python -m venv venv
source venv/Scripts/activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

4. 環境変数を設定

`.env`ファイルを作成し、Anthropic API キーを設定：

```bash
cp .env.example .env
```

`.env`ファイルを編集：

```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

APIキーは [Anthropic Console](https://console.anthropic.com/) で取得できます。

**注意**: APIキーが設定されていない場合、ルールベースのスライド生成にフォールバックします。

## 実行方法

### サーバーの起動

```bash
python main.py
```

または

```bash
uvicorn main:app --reload --port 8000
```

### アプリケーションの利用

1. ブラウザで `http://127.0.0.1:8000` を開く
2. ES入力フォームでセクションを追加し、本文を入力
3. 「構成案を生成」ボタンをクリック
4. スライド確認画面でチャットや直接編集で内容を調整
5. 「PPTXをダウンロード」ボタンでファイルをダウンロード

## プロジェクト構造

```
slide_creater_app/
├── main.py                 # FastAPIバックエンド
├── requirements.txt        # Python依存パッケージ
├── static/
│   ├── index.html         # ES入力フォーム
│   ├── slides.html        # スライド確認・編集画面
│   └── style.css          # 共通スタイル
├── exports/               # 生成されたPPTXファイル（自動作成）
├── README.md              # このファイル
└── CLAUDE.md              # Claude Code用ドキュメント
```

## APIエンドポイント

### `POST /generate`
ES入力から構成案を生成

**リクエスト:**
```json
{
  "sections": [
    {"title": "自己紹介", "content": "私は..."}
  ]
}
```

**レスポンス:**
```json
{
  "slides": [
    {"title": "自己紹介", "bullets": ["項目1", "項目2"]}
  ]
}
```

### `POST /patch`
チャット入力でスライドを編集

**リクエスト:**
```json
{
  "slides": [...],
  "prompt": "最後のスライドを削除"
}
```

**レスポンス:**
```json
{
  "slides": [...]
}
```

### `POST /export`
PPTXファイルを生成

**リクエスト:**
```json
{
  "slides": [...]
}
```

**レスポンス:**
```json
{
  "download_url": "/download/slide_xxxxx.pptx",
  "filename": "slide_xxxxx.pptx"
}
```

## チャット編集の例

- 「最後のスライドを削除」
- 「新しいスライドを追加」
- 「タイトルを〇〇に変更」
- 「もっと具体的に」

## 開発

### 開発モードで起動

```bash
uvicorn main:app --reload --port 8000
```

ファイルを変更すると自動的にサーバーが再起動されます。

### 今後の拡張予定

- MCP (Model Context Protocol) 対応
- スキル（skills）システムの統合
- より高度なAI編集機能
- テンプレート機能

## ライセンス

MIT License

## 作成者

Created with Claude Code
