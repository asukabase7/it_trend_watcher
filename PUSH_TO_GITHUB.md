# GitHubへのプッシュ手順

## 1. GitHubリポジトリの作成

1. GitHubにログインして、https://github.com/new にアクセス
2. リポジトリ名: `it_trend_watcher`（または任意の名前）
3. 説明: "ITトレンド・ウォッチャー & バイブス・コレクター - 自動ITトレンド情報収集ツール"
4. PublicまたはPrivateを選択
5. "Initialize this repository with a README"は**チェックしない**（既にREADMEがあります）
6. "Create repository"をクリック

## 2. リモートリポジトリを追加

```bash
cd /home/asuka/google-drive/Asuka_Dev_Team/02_Projects/it_trend_watcher

# GitHubのリポジトリURLを追加（asukabase7/it_trend_watcher の場合）
git remote add origin https://github.com/asukabase7/it_trend_watcher.git

# またはSSHを使用する場合
# git remote add origin git@github.com:asukabase7/it_trend_watcher.git
```

## 3. プッシュ

```bash
git push -u origin main
```

## 4. GitHub Actionsの設定（オプション）

自動更新を有効にするには：

1. GitHubリポジトリの Settings > Secrets and variables > Actions に移動
2. "New repository secret"をクリック
3. Name: `GEMINI_API_KEY`
4. Value: あなたのGemini APIキー
5. "Add secret"をクリック

これで、GitHub Actionsが毎日自動的にレポートを更新します。

## 5. 確認

プッシュ後、GitHubリポジトリのページで以下を確認：

- ✅ README.mdが正しく表示される
- ✅ `daily_vibes/log_YYYYMMDD.md`ファイルが表示される
- ✅ コードがすべてアップロードされている
