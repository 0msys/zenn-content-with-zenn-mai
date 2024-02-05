# Zenn-MAI: Zenn Mentor and Advisor for Innovation

## リポジトリについて

[こちらの記事](https://zenn.dev/0msys/articles/e658743375e9cf)で紹介したZennの記事執筆を支援するChatBot(Zenn-MAI)のリポジトリです。

## Zenn-MAIを試してみたい場合

試してみたい方は以下の手順で準備をお願いします。

ただし、OpenAIのAPIキーが必要となるので、あらかじめ取得しておいてください。また、動作はVS Codeによる開発コンテナの利用を前提としています。
こちらも併せて準備しておいてください。

---

### 準備

1. このリポジトリをクローンします。

2. ディレクトリに移動します。

3. `/zenn-mai/.streamlit/secrets.toml`にAPIキーを記述します。

```toml
OPENAI_API_KEY="sk-XXXXXXXX"
```

4. VS Codeで開発コンテナを起動します。

5. Zenn CLIをインストールします。

```bash
npm init --yes # プロジェクトをデフォルト設定で初期化
npm install zenn-cli # zenn-cliを導入
npx zenn init # zenn-cliの初期設定
```

参考：[Zenn CLIをインストールする](https://zenn.dev/zenn/articles/install-zenn-cli)

6. 作成された`articles`ディレクトリに、既存の記事(.mdファイル)をコピーします。

7. http://localhost:50001にアクセスすると、ChatBotが使用できます。

### ChatBotの使い方

1. 「執筆支援」か「レビュー」のどちらのモードを使うか選択します。
2. 言語モデルを選択します。
3. 対象の記事のslug(ファイル名)をコピーして貼り付けます。
4. 「レビュー」なら「レビューを開始する」ボタンを押します。「執筆支援」ならそのままチャットを開始できます。

### 作図について

「○○についてフロー図を書いて」のように、作図を指示すると、GraphVizを使ってフロー図を作成します。

もし図に変換する前のコードを確認したい場合は、「チャットのRaw表示」のトグルスイッチをオンにしてください。

### プロンプトについて

`/zenn-mai/src/prompts/`のディレクトリに、各モードで使用するプロンプトの.mdファイルがあります。
必要に応じて編集してください。