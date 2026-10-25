"""会員サイトのページを作る。

  python3 member-site/src/build.py

pages/*.html   … WordPress の「カスタムHTML」ブロックに貼る中身（1ページ1ファイル）
preview.html   … 全ページを1枚で見る確認用（動画は仮の枠で表示）
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = (ROOT / "src" / "member.css").read_text(encoding="utf-8")

# あとで差し替える所。WordPress に貼ったあと、ここだけ書き換えれば済むようにまとめている
LINE_URL = "［LINE公式のURL］"
MAIL = "［メールアドレス］"
BASE = "/member"  # 会員ページの親スラッグ

STEPS = [
    ("step1", "計画する", "高さの内訳と束石の位置"),
    ("step2", "そろえる", "道具と電動工具の安全"),
    ("step3", "基礎をつくる", "束石・直角・支柱"),
    ("step4", "骨組みを組む", "サンドイッチ工法と外周の根太"),
    ("step5", "天板を張って塗る", "線・治具・塗装"),
    ("step6", "長持ちさせる", "点検と塗り直し"),
]


def url(slug=""):
    return f"{BASE}/{slug}/" if slug else f"{BASE}/"


def video(key, title):
    return f"""<div class="wdp-video"><iframe src="https://www.youtube-nocookie.com/embed/{key}" title="{title}" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>
<p class="wdp-video-note">動画が見られないときは、ページを再読み込みしてください。それでも見られない場合はご連絡ください。</p>"""


def hero(eyebrow, title, lead):
    return f"""<div class="wdp-hero"><p class="wdp-eyebrow">{eyebrow}</p><h2>{title}</h2><p>{lead}</p></div>"""


def cards(items):
    out = []
    for c in items:
        num = f'<span class="wdp-num">{c[0]}</span>' if c[0] else ""
        out.append(f'<div class="wdp-card">{num}<h3>{c[1]}</h3><p>{c[2]}</p></div>')
    return '<div class="wdp-grid">' + "".join(out) + "</div>"


def table(head, rows):
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr><th>" + r[0] + "</th>" + "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>" for r in rows)
    return f'<div class="wdp-scroll"><table class="wdp-table"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def checklist(key, items):
    lis = "".join(f'<li><label><input type="checkbox"><span>{i}</span></label></li>' for i in items)
    # チェックはこの端末のブラウザに残る。消えても困らない「目印」として使う
    return f"""<ul class="wdp-check" data-wdp-check="{key}">{lis}</ul>
<p class="wdp-progress" data-wdp-progress="{key}"></p>
<script>(function(){{var k="wdp-check-{key}",l=document.querySelector('[data-wdp-check="{key}"]'),p=document.querySelector('[data-wdp-progress="{key}"]');if(!l)return;var b=l.querySelectorAll("input"),s=[];try{{s=JSON.parse(localStorage.getItem(k)||"[]")}}catch(e){{}}function show(){{var n=0;b.forEach(function(x){{if(x.checked)n++}});p.textContent="できたこと "+n+" / "+b.length}}b.forEach(function(x,i){{x.checked=!!s[i];x.addEventListener("change",function(){{var v=[];b.forEach(function(y){{v.push(y.checked)}});try{{localStorage.setItem(k,JSON.stringify(v))}}catch(e){{}}show()}})}});show()}})();</script>
<p class="wdp-small">チェックは、お使いの端末に記録されます。</p>"""


def help_box(text="つまずいたら、写真を1枚送ってください。あなたの家の状況に合わせてお答えします。"):
    return f"""<div class="wdp-help"><p>{text}</p><a class="wdp-btn wdp-line" href="{LINE_URL}">LINEで相談する</a></div>"""


def nav(prev, nxt):
    a = f'<a href="{url(prev[0])}">← {prev[1]}</a>' if prev else "<span></span>"
    b = f'<a href="{url(nxt[0])}">{nxt[1]} →</a>' if nxt else "<span></span>"
    return f'<nav class="wdp-nav">{a}{b}</nav>'


def sec(title, body, lead=""):
    lead = f'<p class="wdp-lead">{lead}</p>' if lead else ""
    return f'<section><h3 class="wdp-h">{title}</h3>{lead}{body}</section>'


# ---------- ページ ----------

def page_top():
    steps = "".join(
        f'<a class="wdp-step" href="{url(s)}"><span class="wdp-step-no"><small>STEP</small>{i}</span>'
        f'<span class="wdp-step-body"><b>{name}</b><span>{sub}</span></span></a>'
        for i, (s, name, sub) in enumerate(STEPS, 1)
    )
    flow = "".join(
        f"<div><b>{a}</b><em>{b}</em><span>{c}</span></div>"
        for a, b, c in [
            ("準備", "2〜3日", "場所・図面・道具と材料"),
            ("塗装1回目", "1日", "組む前に全部の材料を塗る"),
            ("基礎", "2〜3日", "整地・束石・支柱"),
            ("骨組み", "2〜3日", "根太・根がらみ"),
            ("天板", "1日", "天板を張る"),
            ("塗装2回目", "1日", "表面を仕上げる"),
        ]
    )
    return "\n".join([
        hero("会員ページ", "ようこそ、日曜大工プログラムへ",
             "ご購入ありがとうございます。ここから、あなたの家のウッドデッキづくりが始まります。まずは下の「はじめに」の動画をご覧ください。"),
        sec("はじめに（約5分）", video("ここに動画ID_intro", "はじめに")),
        sec("進め方", cards([
            ("1", "動画を見る", "STEPごとに1本。作業の前の日に見ておくと、当日迷いません。"),
            ("2", "マニュアルで確かめる", "寸法や手順の細かいところは、かんたん版マニュアルと完全版で確認します。"),
            ("3", "チェックして進む", "各STEPのチェックリストに印をつけながら、1つずつ進めます。"),
        ])),
        sec("作業の流れ", f'<div class="wdp-flow">{flow}</div>', "1日まるごと作業するなら9〜12日。日曜日だけなら2〜3か月が目安です。"),
        sec("6つのステップ", f'<div class="wdp-steps">{steps}</div>'),
        sec("最初にやること", f"""<div class="wdp-point"><p><b>図面づくりのために、設置場所の情報を送ってください。</b><br>幅・奥行き・高さの希望と、設置場所の写真をお送りいただくと、あなたの家のサイズの図面一式をお作りします。くわしくは<a href="{url('downloads')}">資料ダウンロード</a>のページをご覧ください。</p></div>"""),
        help_box("作業の途中で困ったことがあれば、180日間、何度でもご相談いただけます。"),
    ])


def step_page(n, slug, name, sub, intro, body, checks):
    prev = ("", "会員トップ") if n == 1 else (STEPS[n - 2][0], f"STEP{n - 1} {STEPS[n - 2][1]}")
    nxt = (STEPS[n][0], f"STEP{n + 1} {STEPS[n][1]}") if n < len(STEPS) else ("support", "相談・質問")
    return "\n".join([
        hero(f"STEP{n}", name, intro),
        sec("解説動画", video(f"ここに動画ID_{slug}", f"STEP{n} {name}")),
        *body,
        sec("チェックリスト", checklist(slug, checks), "全部に印がついたら、次のSTEPへ進みましょう。"),
        help_box(),
        nav(prev, nxt),
    ])


def page_step1():
    return step_page(1, "step1", STEPS[0][1], STEPS[0][2],
        "いちばん大事なのは「計測と基礎」。最初に高さと束石の位置を決めれば、あとの作業は迷いません。",
        [
            sec("この動画の要点", cards([
                ("", "支柱の長さは引き算で決める", "仕上がりの高さから、天板・根太・束石の高さを引いて支柱の長さを出します。支柱は根太より10mmほど短くします。"),
                ("", "束石は1,200mm前後の間隔で", "間隔が広すぎると根太がたわみます。幅3,600×奥行き1,800なら、束石は12個が目安です。"),
                ("", "位置は地面に印をつける", "束石の中心に釘を打つか、スプレーで印をつけておきます。"),
            ])),
            sec("高さの計算例（高さ500mm）", table(["部材", "高さ"], [
                ("天板", "38mm"), ("根太（2段分）", "140×2＝280mm"), ("束石（地上に出る分）", "100mm"),
                ("支柱", "280＋（500−418）＝362mm"),
            ]), "天板38＋根太280＋束石100＝418mm。残りの82mmと根太2段分が支柱の長さです。"),
        ],
        ["設置場所の幅と奥行きを測った", "窓の下から、仕上がりの高さを決めた", "地面の傾きを、水糸と水平器で測った",
         "支柱の長さを計算した", "束石の位置と個数を決めた", "設置場所の情報を送り、図面を依頼した"])


def page_step2():
    return step_page(2, "step2", STEPS[1][1], STEPS[1][2],
        "道具は役割ごとにそろえます。電動工具はDIY用で十分です。材料が届いたら、組む前に1回目の塗装をします。",
        [
            sec("そろえる道具", table(["役割", "道具"], [
                ("掘る", "スコップ（大・小）"),
                ("測る", "メジャー・さしがね・止定規・水平器・水糸"),
                ("印をつける", "鉛筆（赤が見やすい）・チョークライン"),
                ("切る", "電動丸のこ・のこぎり（替刃式）"),
                ("留める", "インパクトドライバー"),
                ("自作する", "タンパー（9cm角＋持ち手）・目地の治具（10mmの木片）"),
            ]), "木材はホームセンターのカットサービスで切ってもらうこともできます。"),
            sec("電動丸のこの安全", cards([
                ("", "真後ろに立たない", "丸のこの斜め左後ろに立ちます。"),
                ("", "刃の交換は電源を抜いて", "角度や深さを変えるときも同じです。"),
                ("", "枕木の位置でキックバックを防ぐ", "切り落とす側が下に落ちる位置で切ります。"),
                ("", "暴れても手を離さない", "刃が止まるまで、しっかり支えます。"),
            ]) + '<div class="wdp-warn" style="margin-top:14px"><p><b>電動丸のこの事故は、60代以上が6割。</b>（消費者庁、2010〜2019年の報告87件）慣れた人ほど、毎回ルールを確かめてください。</p></div>'),
        ],
        ["道具を役割ごとにそろえた", "タンパーと目地の治具（10mm）を作った", "材料を注文した（購入リストで確認）",
         "丸のこの安全ルールを確かめた", "材料が届いたら、全部の材料に1回目の塗装をした（STEP5の動画で塗り方を確認）"])


def page_step3():
    return step_page(3, "step3", STEPS[2][1], STEPS[2][2],
        "束石・直角・支柱。ここをていねいに組めば、ウッドデッキはできたも同然です。",
        [
            sec("束石の下地は、地面のかたさで決める", table(["地面のかたさ", "下地のつくり方"], [
                ("やわらかい<br>（移植ごてで掘れる）", "砕石50〜100mmを突き固め、モルタルで固める"),
                ("ふつう<br>（スコップで掘る）", "砕石50mm＋モルタルで固める"),
                ("かたい<br>（ほぐさないと掘れない）", "埋めて突き固め、モルタルで固めるのがよい"),
                ("コンクリートの上", "水平でなければドライモルタルで調整"),
            ]), "束石は地面に50mmほど埋めて安定させます。モルタルはセメント1：砂3。"),
            sec("直角は「3：4：5」と対角線で", cards([
                ("①", "定規をつくる", "板で90・120・150cmの三角形をつくります。"),
                ("②", "対角線を2本測る", "2本が同じ長さなら直角です。対角線＝√（横の2乗＋縦の2乗）。"),
            ]) + '<div class="wdp-point" style="margin-top:14px"><p><b>例：</b>束石の中心が3,434×1,634なら、対角線は約3,803mm。スマホの電卓で計算できます。</p></div>'),
            sec("支柱は、少し低く、まっすぐに", cards([
                ("10mm", "短く立てる", "水平は、あとで根太で合わせます。支柱どうしはぴったりでなくて大丈夫です。"),
                ("2面", "垂直を見る", "水平器を、向かい合う2つの面に当てます。"),
                ("4本", "羽子板に留める", "小さい穴4か所にビス。四隅の対角線をもう一度測ります。"),
            ]), "水平の確認は、束石・支柱・根太の3回です。"),
        ],
        ["束石の位置を掘り、下地を突き固めた", "束石を据え、モルタルで固めた", "3：4：5の定規と対角線で直角を確かめた",
         "束石の水平を確かめた", "支柱を10mm短く切り、垂直に立てた", "羽子板にビスを留め、対角線をもう一度測った"])


def page_step4():
    return step_page(4, "step4", STEPS[3][1], STEPS[3][2],
        "支柱を根太で挟む「サンドイッチ工法」なら、支柱の高さが多少ばらついても水平が出せます。",
        [
            sec("サンドイッチ工法", cards([
                ("", "サンドイッチ工法（このプログラム）", "支柱を低めに立て、両側から根太で挟んで留めます。水平は根太で合わせます。"),
                ("", "大引工法（すすめない）", "支柱の上に大引をのせます。支柱をすべて同じ高さにそろえないとガタつき、初めての人には難しい方法です。"),
            ]) + '<div class="wdp-warn" style="margin-top:14px"><p><b>弱点は、根太と支柱を留めるビス。</b>デッキの寿命はここで決まります。完成後も定期的にビスの傷みを点検します。</p></div>'),
            sec("いちばん大事：外周の根太", '<div class="wdp-point"><p><b>全体の水平は、外周の根太で決まります。</b>建物側から張り始め、水平器と直角定規で何度も確かめます。1人のときは、クランプや受け台で根太を支えて仮留めします。手伝ってくれる人がいれば、この日に頼みましょう。</p></div>'),
            sec("ビス止めの3つのルール", cards([
                ("3〜4本", "1か所あたり", "最低3本、理想は4本。多すぎても材料費が増えるだけです。"),
                ("×2", "長さは厚みの2倍", "38mmの材なら75mm前後。ステンレス製を使います。"),
                ("下穴", "硬い木だけ", "レッドシダーなら省略してよい。下穴はビスより太くしません。"),
            ])),
        ],
        ["外周の根太を、建物側から張った", "水平器と直角定規で、外周の水平と直角を確かめた", "内側の根太を張った",
         "根がらみを入れた", "ビスは1か所3〜4本、長さは材の厚みの2倍で留めた"])


def page_step5():
    return step_page(5, "step5", STEPS[4][1], STEPS[4][2],
        "張る前に線を引き、全体の長さを確かめます。目地は10mmの治具でそろえ、最後に2回目の塗装で仕上げます。",
        [
            sec("張る前に、線を引いて長さを確かめる", cards([
                ("", "ビスの線を引く", "根太の位置にチョークラインで線。天板1枚につき、根太1本あたりビス2本。140mmの板なら端から30・間80が目安です。"),
                ("", "全体の長さを計算する", "板の幅×枚数＋目地10mm×数。例：140×24＋10×23＝3,590mm。"),
                ("", "仮置きしてから留める", "「その場合わせ」にしません。上に組むほど、ずれは直せなくなります。"),
            ])),
            sec("10mmの治具で、すき間をそろえる", cards([
                ("", "治具", "厚さ10mmの木片を2個以上。上にストッパーをつけると落ちません。"),
                ("", "ビスの頭", "天板の面より1〜2mm沈めます。"),
                ("", "反った板", "両端で10mmを確保。強い反りはバールで（布を当てて）。"),
            ]), "目地10mmは、雨水を流し、風を通して長持ちさせるためです。"),
            sec("塗装は2回", cards([
                ("1回目", "材料が届いたら", "組んだあとは天板の裏・根太・支柱が塗れません。全部の材料を先に塗ります。切った木口は多めに。"),
                ("2回目", "完成したら", "晴れが1〜2日続いた日に。よくかき混ぜ、目地から塗り、木目に沿って薄く塗ります。"),
            ]), "塗料は屋外木部用の木材保護塗料。おすすめは木部浸透性の水性。3.4Lで約17㎡（2回塗り）。"),
        ],
        ["根太の位置にビスの線を引いた", "全体の長さを計算し、両端を決めた", "天板を仮置きして確かめた",
         "10mmの治具で目地をそろえて留めた", "ビスの頭を1〜2mm沈めた", "晴れた日に2回目の塗装をした"])


def page_step6():
    return step_page(6, "step6", STEPS[5][1], STEPS[5][2],
        "完成はゴールではなく、メンテナンスのスタートです。点検と塗り直しを続ければ、10〜15年以上使い続けられます。",
        [
            sec("いちばんの点検ポイントは「目地」", cards([
                ("", "日常", "ほこりを取り、汚れはデッキブラシで水洗いします。"),
                ("", "定期", "接合部とすき間を見て、掃除して塗り直します。"),
                ("", "目地", "天板の側面と根太の上面が、いちばん長く湿ります。水あかを細いブラシで落として塗ります。"),
            ]), "根太と支柱を留めるビスの傷みも、あわせて見てください。"),
            sec("塗り直しの目安", cards([
                ("2年", "最低2年ごと", "天板の上面・側面・木口"),
                ("5年", "最低5年ごと", "天板の下面・根太・根がらみ"),
                ("1〜2年", "早めに", "日や手がよく当たる所"),
            ])),
            sec("完成おめでとうございます", f'<div class="wdp-point"><p><b>完成したデッキの写真を、ぜひ送ってください。</b>一緒に完成を喜ばせてください。完成後のメンテナンスのご相談も受け付けています。</p></div>'),
        ],
        ["完成したデッキの写真を送った", "点検の予定をカレンダーに入れた（2年ごと・5年ごと）",
         "目地とビスの点検をした", "マニュアルのチェックリストに記録を残した"])


def page_downloads():
    def dl(title, text, label, href):
        return f'<div class="wdp-card wdp-dl"><div><h3>{title}</h3><p>{text}</p></div><a class="wdp-btn" href="{href}">{label}</a></div>'
    return "\n".join([
        hero("資料", "資料ダウンロード", "マニュアルはPDFです。スマホで見るときは、ダウンロードしてから開くと読みやすくなります。"),
        sec("マニュアル", '<div class="wdp-steps">' + "".join([
            dl("かんたん版マニュアル（21ページ）", "作業の要点だけをまとめた版。現場に持っていくならこちら。", "ダウンロード", "［かんたん版PDFのURL］"),
            dl("ウッドデッキ実践マニュアル 完全版（108ページ）", "寸法・手順・注意点をすべて載せた版。B5印刷版は別途お届けします。", "ダウンロード", "［完全版PDFのURL］"),
        ]) + "</div>"),
        sec("あなたの家のサイズの図面", f"""<p class="wdp-lead">束石の位置・骨組み・高さの内訳・カット表・購入リストを、あなたの家に合わせてお作りします。次の4つを送ってください。</p>
<ol class="wdp-ol"><li>つくりたいデッキの<b>幅と奥行き</b>（だいたいで大丈夫です）</li><li>窓の下から地面までの<b>高さ</b></li><li>設置場所の<b>写真</b>（正面から1枚、横から1枚）</li><li>使いたい<b>木材</b>（決まっていなければ「おまかせ」）</li></ol>
<div class="wdp-help" style="margin-top:16px"><p>LINEかメールで送ってください。届いた図面は、このページからではなく、LINEかメールでお送りします。</p><a class="wdp-btn wdp-line" href="{LINE_URL}">LINEで送る</a></div>"""),
        sec("材料費の目安を出す", f'<div class="wdp-card wdp-dl"><div><h3>ウッドデッキ計算ツール</h3><p>幅・奥行き・高さを入れるだけで、材料の本数と費用の目安が分かります。</p></div><a class="wdp-btn wdp-ghost" href="［計算ツールのURL］">計算ツールを開く</a></div>'),
        nav(("", "会員トップ"), ("support", "相談・質問")),
    ])


def page_support():
    return "\n".join([
        hero("相談", "相談・質問", "ご購入から180日間、回数無制限でご相談いただけます。地面の傾き、材料の選び方、作業の途中でつまずいたことなど、何でもどうぞ。"),
        sec("相談の方法", cards([
            ("", "LINE（いちばん早い）", "写真をそのまま送れます。"),
            ("", "メール", f"{MAIL}"),
            ("", "Zoom", "顔を見て相談したい方は、LINEかメールで希望の日時をお知らせください。"),
        ]) + f'<p style="margin-top:16px;text-align:center"><a class="wdp-btn wdp-line" href="{LINE_URL}">LINE公式アカウントを友だち追加</a></p>'),
        sec("写真の送り方", '<ol class="wdp-ol"><li><b>全体</b>が分かる写真を1枚（少し離れて）</li><li>困っている<b>部分のアップ</b>を1枚</li><li>寸法が関係するときは、<b>メジャーを当てて</b>撮る</li><li>「STEP3の支柱で」のように、<b>どのSTEPか</b>を書き添える</li></ol>',
            "写真があると、文章だけより正確にお答えできます。"),
        sec("返信の目安", '<div class="wdp-point"><p><b>2日以内にお返事します。</b>作業日の前日までに送っていただくと、当日に間に合います。【要確認：返信日数】</p></div>'),
        nav(("", "会員トップ"), ("guarantee", "返金保証")),
    ])


def page_guarantee():
    return "\n".join([
        hero("保証", "180日間 全額返金保証", "180日間、サポートを受けながら取り組んでも完成しなかった場合は、代金を全額お返しします。"),
        sec("返金保証の詳細", '<div class="wdp-card"><p>【ここに、記述済みの「返金保証の詳細」（条件と手続き）を貼ってください】</p></div>'),
        sec("お申し出の方法", f'<p class="wdp-lead">LINEかメールで「返金保証について」とお知らせください。</p><p style="text-align:center"><a class="wdp-btn wdp-ghost" href="mailto:{MAIL}">メールで連絡する</a></p>'),
        nav(("support", "相談・質問"), ("", "会員トップ")),
    ])


def page_register():
    return "\n".join([
        hero("ご購入ありがとうございます", "会員登録のご案内",
             "このページで会員登録をすると、解説動画とマニュアルが見られる会員ページに入れます。"),
        sec("登録の手順", '<ol class="wdp-ol"><li>下のフォームに、<b>Infotopでご購入時のメールアドレス</b>を入れます</li><li>ユーザー名とパスワードを決めて、登録します</li><li>ご購入を確認して、<b>1日以内に会員ページを使えるようにします</b>【要確認：日数】。使えるようになったらメールでお知らせします</li><li>お知らせが届いたら、ログインページから入ります</li></ol>'),
        '<div class="wdp-point"><p><b>ご購入時と同じメールアドレスで登録してください。</b>違うアドレスで登録すると、ご購入の確認に時間がかかります。</p></div>',
        "<!-- この下に「ショートコード」ブロックを置き、[swpm_registration_form] と入れる -->",
    ])


def page_login():
    return "\n".join([
        hero("会員ページ", "ログイン", "登録したユーザー名とパスワードで入ってください。"),
        "<!-- この下に「ショートコード」ブロックを置き、[swpm_login_form] と入れる -->",
        '<p class="wdp-small" style="margin-top:16px">パスワードを忘れたときは、フォームの下の「パスワードを忘れた方」から再設定できます。まだ登録していない方は、Infotopのご購入完了メールにある登録ページからどうぞ。</p>',
    ])


PAGES = [
    # (ファイル名, WordPressのページ名, スラッグ, 中身, 会員限定か)
    ("00-register", "会員登録", "register", page_register, False),
    ("01-login", "ログイン", "login", page_login, False),
    ("10-top", "会員トップ", "member", page_top, True),
    ("11-step1", "STEP1 計画する", "member/step1", page_step1, True),
    ("12-step2", "STEP2 そろえる", "member/step2", page_step2, True),
    ("13-step3", "STEP3 基礎をつくる", "member/step3", page_step3, True),
    ("14-step4", "STEP4 骨組みを組む", "member/step4", page_step4, True),
    ("15-step5", "STEP5 天板を張って塗る", "member/step5", page_step5, True),
    ("16-step6", "STEP6 長持ちさせる", "member/step6", page_step6, True),
    ("20-downloads", "資料ダウンロード", "member/downloads", page_downloads, True),
    ("21-support", "相談・質問", "member/support", page_support, True),
    ("22-guarantee", "返金保証", "member/guarantee", page_guarantee, True),
]


def main():
    out = ROOT / "pages"
    out.mkdir(exist_ok=True)
    blocks = []
    for fname, title, slug, fn, members in PAGES:
        body = f'<div class="wdp">\n{fn()}\n</div>\n'
        (out / f"{fname}.html").write_text(body, encoding="utf-8")
        blocks.append((fname, title, slug, body, members))

    # 確認用：リンクはページ内の見出しへ、動画は仮の枠に置き換える
    def localize(body):
        body = re.sub(r'href="/member/([a-z0-9]*)/?"', lambda m: f'href="#p-{m.group(1) or "member"}"', body)
        return re.sub(r'<iframe src="[^"]*embed/([^"]*)" title="([^"]*)"[^>]*></iframe>',
                      lambda m: f'<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#f5f3ec;gap:6px"><span style="font-size:42px">▶</span><span>{m.group(2)}</span><span style="font-size:12px;opacity:.7">（YouTube動画がここに入ります）</span></div>', body)

    toc = "".join(f'<a href="#p-{s.split("/")[-1]}">{t}</a>' for _, t, s, _, _ in blocks)
    secs = "".join(
        f'<article id="p-{s.split("/")[-1]}" class="pv-page"><header class="pv-head"><b>{html.escape(t)}</b>'
        f'<span>/{s}/ ・ {"会員限定" if m else "だれでも見られる"} ・ pages/{f}.html</span></header>{localize(b)}</article>'
        for f, t, s, b, m in blocks
    )
    preview = f"""<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>会員サイト プレビュー</title>
<style>
body{{margin:0;background:#e9e6dd;font-family:"Hiragino Kaku Gothic ProN","Noto Sans JP",sans-serif}}
.pv-toc{{position:sticky;top:0;z-index:2;background:#1b231e;display:flex;gap:4px;overflow-x:auto;padding:8px 12px}}
.pv-toc a{{flex:none;color:#f5f3ec;text-decoration:none;font-size:13px;padding:6px 10px;border-radius:6px}}
.pv-toc a:hover{{background:#2c6849}}
.pv-page{{background:#fff;max-width:960px;margin:24px auto;padding:32px 40px 40px;border-radius:8px;scroll-margin-top:56px}}
.pv-head{{display:flex;flex-wrap:wrap;gap:4px 12px;align-items:baseline;border-bottom:1px dashed #ccc;padding-bottom:10px;margin-bottom:24px;font-size:13px;color:#777}}
.pv-head b{{font-size:15px;color:#1b231e}}
@media (max-width:600px){{.pv-page{{margin:12px 0;padding:20px 16px;border-radius:0}}}}
{CSS}
</style></head><body><nav class="pv-toc">{toc}</nav>{secs}</body></html>"""
    (ROOT / "preview.html").write_text(preview, encoding="utf-8")
    print(f"{len(blocks)} pages")


if __name__ == "__main__":
    main()
