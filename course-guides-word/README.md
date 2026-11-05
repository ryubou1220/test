# 週末DIY 5ステップ講座　解説書（Word版）

| フォルダ | 中身 |
|---|---|
| `詳しい版/` | STEP1〜4の詳しい解説書（各11〜14ページ）。図面・工程ごとの図、よくある失敗、困ったときの表、よくある質問、作業の記録欄つき |
| `既存版/` | `course-guides/src/step1〜4.md`（festive-noether ブランチ）をそのままWordにしたもの |
| `src/` | 詳しい版を作るスクリプトと図（図は `course/` の教材から書き出したもの） |

詳しい版を作り直すとき（`src/step1.js`〜`step4.js` の文章を直してから）：

```bash
cd course-guides-word/src
FIG_DIR=$PWD/figs NODE_PATH=$(npm root -g) node run.js ../詳しい版 step1 step2 step3 step4
```
