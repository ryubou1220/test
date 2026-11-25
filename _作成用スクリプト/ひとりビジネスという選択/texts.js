const fs = require("fs");
const { titleBlock, blocks, save } = require("./lib");
const OUT = process.argv[2];
const L = JSON.parse(fs.readFileSync("texts.json", "utf8"));
(async () => {
  for (const l of L) {
    const title = `第${l.no}講義　${l.name}`;
    const c = [...titleBlock(title, l.theme), ...blocks(l.text)];
    await save(`${OUT}/第${l.no}講義_${l.name}_講義テキスト.docx`, c, { title: `${title}　講義テキスト`, footer: `ひとりビジネスという選択｜${title}` });
  }
})();
