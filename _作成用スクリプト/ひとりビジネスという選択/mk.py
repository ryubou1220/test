import json,sys,subprocess,os,glob
sys.path.insert(0,'.')
L=[]
for f in sys.argv[2:]:
    g={}; exec(open(f,encoding='utf8').read(),g); L+=g['L']
os.makedirs(sys.argv[1],exist_ok=True)
for l in L:
    j=f"{sys.argv[1]}/s{l['no']}.json"
    json.dump({"footer":f"ひとりビジネスという選択 ｜ 第{l['no']}講義　{l['name']}","slides":l["slides"]},open(j,'w',encoding='utf8'),ensure_ascii=False)
    out=f"{sys.argv[1]}/第{l['no']}講義_{l['name']}.pptx"
    subprocess.run(["python3","-I","build_deck.py","/home/user/test/特典/第2講義_マインドセット編.pptx",out,j],check=True)
