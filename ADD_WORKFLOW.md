# GitHub Actionsワークフローの追加方法

## 方法1: Personal Access Tokenのスコープを更新（推奨）

1. GitHubにログインして、https://github.com/settings/tokens にアクセス
2. 使用しているPersonal Access Tokenを編集
3. `workflow`スコープにチェックを入れる
4. "Update token"をクリック
5. 以下のコマンドでワークフローファイルを追加：

```bash
cd /home/asuka/google-drive/Asuka_Dev_Team/02_Projects/it_trend_watcher
git add .github/workflows/daily-update.yml
git commit -m "Add GitHub Actions workflow for daily updates"
git push
```

## 方法2: GitHubのWeb UIから追加

1. GitHubリポジトリのページで、`.github/workflows/`フォルダを作成
2. `daily-update.yml`ファイルを新規作成
3. 以下の内容をコピー＆ペースト：

```yaml
name: Daily Update

on:
  schedule:
    # 毎日日本時間の朝9時に実行（UTC 0:00）
    - cron: '0 0 * * *'
  workflow_dispatch:  # 手動実行も可能

jobs:
  update:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run IT Trend Watcher
      env:
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
      run: |
        python3 src/main.py
    
    - name: Commit and push changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add daily_vibes/*.md
        git diff --staged --quiet || git commit -m "Auto-update: $(date +'%Y-%m-%d')"
        git push
```

4. "Commit new file"をクリック

## 方法3: SSH認証を使用

SSH認証を使用している場合、ワークフローファイルを直接プッシュできます：

```bash
cd /home/asuka/google-drive/Asuka_Dev_Team/02_Projects/it_trend_watcher

# SSHリモートに変更（既にHTTPSを使用している場合）
git remote set-url origin git@github.com:asukabase7/it_trend_watcher.git

# ワークフローファイルを追加
git add .github/workflows/daily-update.yml
git commit -m "Add GitHub Actions workflow for daily updates"
git push
```

## GitHub Actionsの設定

ワークフローファイルを追加した後：

1. リポジトリの Settings > Secrets and variables > Actions に移動
2. "New repository secret"をクリック
3. Name: `GEMINI_API_KEY`
4. Value: あなたのGemini APIキー
5. "Add secret"をクリック

これで、GitHub Actionsが毎日自動的にレポートを更新します。
