"""仅按标题关键词作可复核的多标签统计，不据此诊断性格。"""
from pathlib import Path
from collections import Counter
import csv, json, re

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'小红书收藏数据集_20261028'
RULES = {
 '数学与竞赛学习':r'数学|数院|数分|高代|高等代数|微积分|高数|代数|几何|数模|建模|美赛|CMC|丘成桐|丘维声|黎曼|贝叶斯|统计学|拓扑|模形式|(?<![A-Za-z])ODE(?![A-Za-z])|偏微分|幂方程|矩阵论|张寿武',
 '升学职业与学习方法':r'保研|跨保|绩点|均绩|科研|实验室|论文|实习|就业|找工作|转码|算法岗|转算法|前景|出路|培养方案|选课|抢课|备考|四级|六级|英语|高考|强基|国奖|本科生|研究生|硕士|博士|考研|清北|清华|老师|教师',
 '文学历史与文艺':r'文学|历史|古言|小说|原著|诗|苏轼|苏东坡|余秋雨|徐志摩|杨绛|三国|陆逊|诸葛|孙权|张辽|王朝|南北朝|明孝陵|海昏侯|贞观|长孙|皇后|武则天|左传|岳阳楼|湘夫人|秦时|诛仙|凡雪|雪琪|小凡|鬼厉|道玄|凤囚凰|择天记|仙剑|不良人|姬如雪|天行九歌|聊斋|国漫|元尊|绍宋|剑来|红楼|林黛玉|古典|美学|会饮|哲学|卢照邻|书店|读书会|阅读|看书|图书馆|鼓楼摩崖|鼓浪文学|文学大奖|作文|漫画|画法|画一只|绘画|孝陵|陈寿|封神',
 '现实亲密关系':r'恋爱|男朋友|女朋友|男友|女友|情侣|男追女|追女生|追人|喜欢的人|男生怎么追|告白|表白|crush|脱单|母单|婚后|结婚|初恋|暧昧|亲密|男女交往|未婚|纯爱|爱情|恋人|男孩子谈恋爱|妻子|爱人|真正的爱|我们的曾经|爱是克制|最舒服的关系',
 '社交表达与家庭':r'交友|扩列|搭讪|聊天|发消息|朋友|友情|亲情|父母|原生家庭|爸爸妈妈|沟通|阴阳怪气|不聊心事|聊心事|见面的最高礼仪|社会生存|大学最舒服的关系',
 'AI与数字工具':r'(?<![A-Za-z])AI(?![A-Za-z])|人工智能|chatgpt|codex|github|agent|gpt|gemini|python|代码|编程|latex|beamer|markdown|onenote|语雀|笔记软件|软件做笔记|华为自带笔记|电脑小技巧|硬核网站|电脑VS|图片风格转化|SVG|转中文|题库|论文排版',
 '情绪与人生思考':r'焦虑|内耗|迷茫|低谷|自救|情绪|解压|痛苦|心态|反思|人生|生命|努力|失利|没出息|有出息|意义|躺不平|用力过猛|重新学会学习|给20岁|给二十岁|三十岁以上|40岁的男人|给你温暖|不再焦虑',
 '形象运动与健康':r'美白|冷白皮|毛孔|关节黑|变帅|丑男|发型|薄肌|健身|运动|身体素质|引体|减脂|掉秤|饮食|增到|体重|仰卧起坐|小腹|锻炼|精华|防晒|晒不黑|脾胃|肠胃|中药|中医|健康|环校跑|缩毛孔',
 '生活地点与实用经验':r'厦门|厦大|XMU|xmuer|xmu|漳州|漳浦|福建|福州|泉州|南京|宁波|都江堰|青城山|旅行|旅游|住宿|自习|咖啡|餐厅|植物园|宿舍|收纳|打包|拍摄|充电宝|耳机|快充|礼物|炒饭|牛肉羹|好吃|做法|科目一|科一|交通标志|博物馆|高铁|鼓山|金门|周末.*活动',
 '动物轻松与日常审美':r'猫|小狗|狗狗|柯基|卡皮巴拉|宠物|养宠|头像|壁纸|表情包|咪的|咪渴|拼豆|简笔画|搞怪|盲盒|猪猪侠|动物|肉很多',
}
FICTION = re.compile(r'诛仙|凡雪|雪琪|小凡|鬼厉|道玄|文学史|古言|小说|原著|国漫|择天记|钗头凤|凤囚凰|仙剑|诗|氓|陈晓旭|林黛玉|影视|剧|BE文学|徐有容|姬如雪|秦时', re.I)

def write_csv(path, rows, fields):
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)

def main():
    with (OUT/'当前收藏.csv').open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    counts = Counter(); labelled = []; examples = {}
    for row in rows:
        title = row['标题']; matches = {}
        for topic, rule in RULES.items():
            found = sorted(set(re.findall(rule, title, re.I)))
            if topic == '现实亲密关系' and FICTION.search(title):
                found = []
            if found:
                matches[topic] = found; counts[topic] += 1
                examples.setdefault(topic, []).append({'序号':row['目录序号_从1开始'],'标题':title,'链接':row['笔记链接']})
        labelled.append({'笔记ID':row['笔记ID'], '目录序号':row['目录序号_从1开始'], '标题':title,
                         '命中主题_允许重叠':'；'.join(matches) or '未命中规则',
                         '命中词':json.dumps(matches, ensure_ascii=False), '标签性质':'标题关键词规则_待人工复核',
                         '本人是否认同_待填写':'', '收藏目的_待填写':'', '是否实际使用_待填写':''})
    stats = [{'主题':topic,'命中条数':count,'占本轮631条比例':round(count/len(rows),6),'统计口径':'多标签标题关键词；不同主题不可相加'} for topic,count in counts.most_common()]
    write_csv(OUT/'主题关键词标记_待复核.csv', labelled, list(labelled[0]))
    write_csv(OUT/'主题关键词统计.csv', stats, list(stats[0]))
    (OUT/'主题标记规则.json').write_text(json.dumps({'rules':RULES,'romance_fiction_exclusion':FICTION.pattern,'denominator':len(rows),'unmatched':sum(r['命中主题_允许重叠']=='未命中规则' for r in labelled),'examples':{k:v[:6] for k,v in examples.items()}},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'denominator':len(rows),'counts':stats,'unmatched':sum(r['命中主题_允许重叠']=='未命中规则' for r in labelled)},ensure_ascii=False,indent=2))

if __name__ == '__main__': main()
