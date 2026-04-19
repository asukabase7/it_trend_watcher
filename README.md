# ITトレンド・ウォッチャー & バイブス・コレクター

**IT Trend Watcher & Vibes Collector**

自動的にITトレンド情報を収集し、AIで要約してMarkdown形式で出力するツールです。

An automated tool that collects IT trend information and summarizes it using AI, outputting in Markdown format.

---

## 🌟 なぜこのツールが2026年のエンジニアに必要か / Why This Tool is Essential for Engineers in 2026

### 🇯🇵 日本語

2026年、エンジニアを取り巻く情報環境はますます複雑になっています。日々、SaaS、AI、Python、Vibe Codingなどの最新動向が世界中から発信され、それらを追いかけるだけでも大変な作業です。

このツールは、以下の理由で現代のエンジニアに不可欠です：

1. **時間の節約**: 複数の情報源を手動でチェックする必要がなくなります
2. **言語の壁を越える**: 英語の情報を自動的に日本語で要約し、理解しやすくします
3. **継続的な学習**: 毎日のトレンドを自動的に記録し、知識の蓄積を支援します
4. **オープンソース**: GitHubに「落とし物」として公開され、誰でも利用・改善できます
5. **プロフェッショナルな品質**: 実務未経験とは思えないクリーンコードで、学習にも最適です

### 🇺🇸 English

In 2026, the information environment surrounding engineers is becoming increasingly complex. Daily updates on SaaS, AI, Python, Vibe Coding, and other cutting-edge trends are being published worldwide, making it a daunting task to keep up with them all.

This tool is essential for modern engineers for the following reasons:

1. **Time Savings**: Eliminates the need to manually check multiple information sources
2. **Language Barrier Removal**: Automatically summarizes English information into Japanese, making it easier to understand
3. **Continuous Learning**: Automatically records daily trends, supporting knowledge accumulation
4. **Open Source**: Published as a "found item" on GitHub, available for anyone to use and improve
5. **Professional Quality**: Clean code that doesn't look like it was written by someone without practical experience, perfect for learning

---

## ✨ 機能 / Features

- 🌐 **TechCrunch**: 世界の最新テックニュースを収集（英語→Gemini AI で日本語要約）
- 📘 **Zenn**: 日本語テック記事を収集
- 📝 **Qiita**: 日本語テック記事を収集
- 🤖 **AI要約**: Gemini API を使用して英語コンテンツを3行のプロエンジニア風日本語で要約
- 📄 **Markdown出力**: GitHubで美しく表示されるMarkdown形式で日次レポートを生成
- 🔔 **Slack通知**（任意）: 実行完了時に収集件数・要約結果を投稿

---

## 🚀 セットアップ / Setup

### 前提条件 / Prerequisites

- Python 3.8以上
- Google Generative AI APIキー（[Google AI Studio](https://aistudio.google.com/)で無料取得可能）

### インストール / Installation

```bash
# リポジトリをクローン
git clone https://github.com/asukabase7/it_trend_watcher.git
cd it_trend_watcher

# セットアップスクリプトを実行（仮想環境の作成と依存パッケージのインストール）
bash setup.sh

# 環境変数を設定
cp .env.example .env
# .envファイルを編集してGEMINI_API_KEYを設定
```

**注意**: Ubuntuなどのシステムでは、仮想環境を使用する必要があります。`setup.sh`スクリプトが自動的に仮想環境を作成し、依存パッケージをインストールします。

### 環境変数の設定 / Environment Variables

`.env`ファイルに以下を設定してください：

```env
GEMINI_API_KEY=your_api_key_here
```

APIキーは [Google AI Studio](https://aistudio.google.com/) で取得できます。無料枠も利用可能です。

---

## 📖 使い方 / Usage

### 手動実行 / Manual Execution

**方法1: 仮想環境を使用（推奨）**

```bash
# 仮想環境付きで実行（自動的に仮想環境をアクティベート）
bash run_with_venv.sh
```

**方法2: 手動で仮想環境をアクティベート**

```bash
# 仮想環境をアクティベート
source ~/.venv_it_trend_watcher/bin/activate

# 実行
python3 run.py
# または
python3 src/main.py

# 仮想環境をデアクティベート（終了時）
deactivate
```

**方法3: システムのPythonを使用（仮想環境が不要な場合）**

```bash
python3 run.py
```

### 自動実行（Cronジョブ） / Automated Execution (Cron Job)

毎日指定時刻に自動実行する場合：

```bash
# crontabを編集
crontab -e

# 毎日朝9時に実行する例
0 9 * * * cd /path/to/it_trend_watcher && python3 src/main.py
```

---

## 📁 プロジェクト構造 / Project Structure

```
it_trend_watcher/
├── src/
│   ├── collectors/          # データ収集モジュール
│   │   ├── techcrunch_collector.py
│   │   ├── zenn_collector.py
│   │   ├── qiita_collector.py
│   │   ├── nikkei_collector.py   # (将来利用)
│   │   └── twitter_collector.py  # (将来利用)
│   ├── processors/           # データ処理モジュール
│   │   └── gemini_summarizer.py
│   ├── notifiers/            # 通知モジュール
│   │   └── slack.py
│   ├── writers/              # 出力モジュール
│   │   └── markdown_writer.py
│   └── main.py               # メイン実行スクリプト
├── config/                   # 設定管理
│   └── settings.py
├── .github/workflows/        # GitHub Actions
│   └── daily-update.yml
├── daily_vibes/              # 出力ディレクトリ
│   └── log_YYYYMMDD.md
├── .env.example              # 環境変数テンプレート
├── requirements.txt          # 依存パッケージ
├── run.py                    # エントリーポイント
├── setup.sh                  # セットアップスクリプト
└── README.md                 # このファイル
```

---

## 📊 出力例 / Output Example

`daily_vibes/log_20260129.md` のような形式で出力されます：

```markdown
# ITトレンド・ウォッチャー - 2026年01月29日

## 🇯🇵 日経電子版テック面

### [記事タイトル](URL)
- **公開日**: 2026-01-29 10:00
- **概要**: ...

## 🐦 X（Twitter）

### @karpathy
- **投稿**: [投稿内容]
  - **投稿日**: 2026-01-29 10:00
  - **URL**: [URL]
  - **要約**: [Gemini要約結果]

## 🌐 TechCrunch

### [記事タイトル](URL)
- **公開日**: 2026-01-29 10:00
- **要約**: [Gemini要約結果]
```

---

## 🛠️ 技術スタック / Tech Stack

- **Python 3.8+**: メイン言語
- **feedparser**: RSSフィード解析
- **requests**: HTTPリクエスト
- **beautifulsoup4**: HTMLパース
- **google-genai**: Gemini API統合（新SDK）
- **python-dotenv**: 環境変数管理

---

## 🔧 カスタマイズ / Customization

### 収集対象の変更 / Changing Collection Targets

`config/settings.py`を編集して、収集対象を変更できます：

```python
# Twitter収集対象アカウント
TWITTER_TARGETS = [
    'karpathy',  # Andrej Karpathy
    'jasonlk',   # Jason Lemkin
    # ここに追加したいアカウントを追加
]

# 各ソースから取得する最大記事数
MAX_ARTICLES_PER_SOURCE = 10
MAX_TWEETS_PER_USER = 5
```

---

## 📤 GitHubへの公開 / Publishing to GitHub

### クイックスタート / Quick Start

```bash
# 1. GitHubでリポジトリを作成（https://github.com/new）

# 2. リモートを追加
git remote add origin https://github.com/YOUR_USERNAME/it_trend_watcher.git

# 3. プッシュ
git push -u origin main
```

### GitHub Actions（自動実行）の設定

1. リポジトリの **Settings > Secrets and variables > Actions** を開く
2. **New repository secret** で以下を追加：
   - `GEMINI_API_KEY`: Google AI Studio で取得したキー（必須）
   - `SLACK_WEBHOOK_URL`: Slack の Incoming Webhook URL（任意）
3. Actions タブでワークフローを有効化

設定後、毎日 UTC 0:00（JST 9:00）に自動実行され、`daily_vibes/log_YYYYMMDD.md` がコミットされます。

## 🤝 コントリビューション / Contribution

このプロジェクトは「落とし物」として公開されています。自由にフォークして、改善してください！

This project is published as a "found item". Feel free to fork and improve it!

---

## 📝 ライセンス / License

このプロジェクトはオープンソースです。自由に使用・改変してください。

This project is open source. Feel free to use and modify it.

---

## 🙏 謝辞 / Acknowledgments

- [Google Generative AI](https://ai.google.dev/) - Gemini API
- [日経電子版](https://www.nikkei.com/) - ニュースソース
- [TechCrunch](https://techcrunch.com/) - ニュースソース
- [Nitter](https://github.com/zedeus/nitter) - Twitter RSS取得の代替手段

---

## 📧 連絡先 / Contact

GitHub: [@asukabase7](https://github.com/asukabase7)

---

**Happy Coding! 🚀**
