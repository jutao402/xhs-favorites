from pathlib import Path
from datetime import datetime, timezone
import csv, json

root=Path(__file__).resolve().parent
folder=root/'小红书收藏数据集_20261028'
dataset=json.loads((folder/'收藏数据集.json').read_text(encoding='utf-8'))
with (folder/'主题关键词标记_待复核.csv').open(encoding='utf-8-sig',newline='') as f:
    annotations={r['笔记ID']:r for r in csv.DictReader(f)}
rows=[]
for r in dataset['records']:
    annotation=annotations.get(r['笔记ID'])
    topics=annotation['命中主题_允许重叠'].split('；') if annotation else ['未命中规则']
    rows.append({'noteId':r['笔记ID'],'order':r['目录序号_从1开始'] or None,
                 'title':r['标题'] or '（标题为空）','author':r['作者'],'url':r['笔记链接'],
                 'state':'本轮目录' if r['本轮是否出现'] else '历史补充','topics':topics,
                 'matchedWords':json.loads(annotation['命中词']) if annotation else {},'cardText':r['卡片原文']})
source={'label':'小红书收藏卡片与本地整合数据','files':['当前收藏.csv','历史补充.csv','主题关键词标记_待复核.csv','质量检查.json'],
        'links':[{'label':'来源主页','url':'https://www.xiaohongshu.com/user/profile/668f9e18000000000f036319'}],
        'filters':['采集日期：2026-10-28（北京时间）','本轮631条；历史补充2条；另289条未核实'],
        'metricDefinitions':[{'label':'主题命中条数','definition':'当前筛选范围内，标题关键词命中该主题的去重笔记数。允许多标签，主题不可相加。'},
                             {'label':'目录序号','definition':'本轮网页中的列表位置，不是收藏或发布时间。'}],
        'caveats':['部分数据，不得外推为全部920条收藏的比例。','标题关键词规则初分，未人工逐条语义确认。','未采集正文与图片；收藏不等于认同。'],
        'evidenceFlow':[{'title':'授权网页读取','detail':'通过 Playwright Extension 读取本人收藏/笔记页面已加载卡片的标题、真实编号、作者和链接。'},
                        {'title':'整合与标记','detail':'整合最终数据集.py 按真实笔记ID去重，保留631条当前记录与2条历史补充；分析收藏主题.py 按保留规则多标签匹配标题。'}]}
snapshot={'surface':'dashboard','title':'我的收藏','generatedAt':datetime.now(timezone.utc).isoformat(),'status':'reviewed-partial','buildStatus':'creating',
          'exportPreferences':{'selected':None,'destinations':[]},'filters':[],
          'queries':{'notes':{'rows':rows,'source':source},
                     'coverage':{'rows':[{'status':'本轮已读','count':631},{'status':'尚未核实','count':289}],
                                 'source':{**source,'label':'页面计数与本轮采集覆盖','metricDefinitions':[{'label':'覆盖范围','definition':'页面显示920条，本轮已读取631条，差额289条尚未核实；不含2条历史补充。'}]}}}}
target=root/'可视化数据.json'
target.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'rows':len(rows),'current':sum(r['state']=='本轮目录' for r in rows),'snapshot':str(target)},ensure_ascii=False))
