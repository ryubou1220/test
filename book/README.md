# ものづくりが人間のキモ（肝）という話

電子書籍の原稿リポジトリです。

## 構成

```
book/
├── outline.md        # 企画・構成メモ、今後のTODO
├── metadata.yaml     # 書誌情報（タイトル・著者名など）
├── style.css         # EPUB 用スタイル
├── Makefile          # ビルド
├── manuscript/       # 本文（ファイル名順に結合されます）
│   ├── 00-preface.md       はじめに
│   ├── 01-homo-faber.md    第1章 人間は「つくる動物」である
│   ├── 02-hands.md         第2章 手は外に出た脳である
│   ├── 03-failure.md       第3章 思いどおりにならないから、面白い
│   ├── 04-for-someone.md   第4章 つくることは、誰かを想うこと
│   ├── 05-consumer.md      第5章 「買うだけ」の暮らしで失ったもの
│   ├── 06-ai-era.md        第6章 AI の時代にこそ、つくる
│   ├── 07-practice.md      第7章 今日からできる、小さなものづくり
│   └── 99-afterword.md     おわりに
└── dist/             # ビルドした EPUB
```

## ビルド

[pandoc](https://pandoc.org/) が必要です。

```bash
cd book
make epub    # dist/monozukuri-kimo.epub を生成
make count   # 章ごとの文字数を表示
```

表紙画像を `book/cover.jpg` に置くと、自動で表紙として組み込まれます。
