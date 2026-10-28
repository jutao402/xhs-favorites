"""将本轮目录与历史 DOM 采集整合；只按真实笔记 ID 合并。"""
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone, timedelta
import csv, hashlib, json, re, shutil, sqlite3, zipfile

ROOT = Path(__file__).resolve().parent
CURRENT = ROOT / 'Edge采集批次_20261028'
OUT = ROOT / '小红书收藏数据集_20261028'
SOURCE = 'https://www.xiaohongshu.com/user/profile/668f9e18000000000f036319?tab=fav&subTab=note'

def write_csv(path, rows, fields):
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def read_batches(directory):
    for path in sorted(directory.glob('batch-*.json')):
        item = json.loads(path.read_text(encoding='utf-8'))
        yield path, item

def clean(card):
    links = [{'text': a.get('text', ''), 'href': a.get('href', '').split('?')[0].split('#')[0]} for a in card.get('links', [])]
    return {**card, 'links': links}

def main():
    OUT.mkdir(exist_ok=True)
    all_records = {}
    provenance = defaultdict(set)
    timestamps = defaultdict(set)
    current = {}
    positions = defaultdict(set)
    id_positions = defaultdict(set)
    total = 0
    directories = [ROOT/'采集批次'] + sorted(p for p in ROOT.glob('Edge采集批次_*') if p != CURRENT) + [CURRENT]
    for directory in directories:
        for path, item in read_batches(directory):
            if directory == CURRENT:
                total = item.get('displayed_total') or total
            for raw_card in item.get('cards', []):
                card = clean(raw_card)
                note_id = card.get('note_id') or ''
                if not re.fullmatch(r'[0-9a-f]{24}', note_id):
                    raise ValueError(f'非真实笔记编号：{path.name}')
                source = f'{directory.name}/{path.name}'
                provenance[note_id].add(source)
                observed = item.get('observed_at') or card.get('observed_at')
                if observed:
                    timestamps[note_id].add(observed)
                all_records[note_id] = {**card, 'source_batch': source}
                if directory == CURRENT:
                    current[note_id] = {**card, 'source_batch': source}
                    positions[card['index']].add(note_id)
                    id_positions[note_id].add(card['index'])
    conflicts = {i: sorted(ids) for i, ids in positions.items() if len(ids) > 1}
    moved = {key: sorted(indices) for key, indices in id_positions.items() if len(indices) > 1}
    gaps = sorted(set(range(total)) - set(positions))
    if conflicts or moved:
        raise ValueError('本轮存在位置冲突；不能生成完成数据集')
    endpoint_path = CURRENT/'终点核对.json'
    endpoint = json.loads(endpoint_path.read_text(encoding='utf-8')) if endpoint_path.exists() else {}
    complete = len(current) == total and not gaps
    fields = ['笔记ID', '本轮是否出现', '目录序号_从1开始', '标题', '作者', '笔记链接', '卡片原文', '观察时间最早_已有时间戳', '观察时间最近_已有时间戳', '来源批次', '来源批次数', '正文是否采集']
    def row(note_id, card):
        links = card.get('links', [])
        urls = [a['href'] for a in links if note_id in a['href'] and '/user/profile/' not in a['href']]
        if not urls:
            urls = [a['href'] for a in links if note_id in a['href']]
        url = urls[0] if urls else ''
        if url.startswith('/'):
            url = 'https://www.xiaohongshu.com' + url
        authors = [a['text'].strip() for a in links if re.fullmatch(r'/user/profile/[0-9a-f]{24}', a['href']) and a['text'].strip()]
        times = sorted(timestamps[note_id])
        return {'笔记ID': note_id, '本轮是否出现': int(note_id in current),
                '目录序号_从1开始': current[note_id]['index']+1 if note_id in current else '',
                '标题': card.get('title', ''), '作者': authors[-1] if authors else '',
                '笔记链接': url, '卡片原文': card.get('text', ''),
                '观察时间最早_已有时间戳': times[0] if times else '', '观察时间最近_已有时间戳': times[-1] if times else '',
                '来源批次': card['source_batch'], '来源批次数': len(provenance[note_id]), '正文是否采集': 0}
    current_rows = [row(key, card) for key, card in sorted(current.items(), key=lambda pair:pair[1]['index'])]
    historical = [row(key, card) for key, card in sorted(all_records.items()) if key not in current]
    merged = current_rows + historical
    assert len(merged) == len({r['笔记ID'] for r in merged})
    assert all('?' not in r['笔记链接'] and 'xsec_token' not in r['笔记链接'] for r in merged)
    quality = {'采集日期_北京时间':'2026-10-28', '来源页面':SOURCE,
               '页面显示收藏数':total, '本轮目录条数':len(current_rows), '历史补充条数':len(historical),
               '整合去重条数':len(merged), '本轮位置缺口_从0开始':gaps, '目录位置冲突':conflicts,
               '编号位置变化':moved, '本轮目录计数完全匹配':complete, '终点核对':endpoint,
               '本轮空标题数':sum(not r['标题'].strip() for r in current_rows),
               '本轮空作者数':sum(not r['作者'].strip() for r in current_rows),
               '本轮空链接数':sum(not r['笔记链接'].strip() for r in current_rows),
               '整合编号重复数':len(merged)-len({r['笔记ID'] for r in merged}),
               '正文与图片已下载':False, '发布时间与收藏时间已获取':False,
               '历史补充解释':'此前真实读取过，本轮目录未出现；不能据此确定已取消收藏或被删除。',
               '观察时间解释':'网页被读取的时间，不是发布或收藏时间；无时间戳的早期观察不计入时间范围。',
               '来源批次数解释':'采集时同一卡片可能反复出现；该数值不能表示用户收藏或浏览频次。'}
    write_csv(OUT/'当前收藏.csv', current_rows, fields)
    write_csv(OUT/'历史补充.csv', historical, fields)
    write_csv(OUT/'整合收藏.csv', merged, fields)
    (OUT/'收藏数据集.json').write_text(json.dumps({'metadata':quality, 'records':merged}, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT/'质量检查.json').write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding='utf-8')
    current_paths = list(CURRENT.glob('batch-*.json'))
    checkpoint = {'status':{'batch':max(int(p.stem.split('-')[1]) for p in current_paths), 'displayed_total':total,
                  'observed_records':len(current), 'missing_position_count':len(gaps), 'all_card_slots_observed':complete},
                  'records':sorted(current.values(), key=lambda c:c['index']), 'conflicts':[], 'missing_positions':gaps}
    (CURRENT/'实时采集数据.json').write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding='utf-8')
    raw_paths = current_paths + [ROOT/r['来源批次'] for r in historical]
    for source_path in sorted(set(raw_paths)):
        destination = OUT/'原始采集批次'/source_path.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)
    shutil.copy2(endpoint_path, OUT/'原始采集批次'/'终点核对.json')
    db = sqlite3.connect(OUT/'收藏数据.sqlite')
    db.execute('CREATE TABLE IF NOT EXISTS notes(note_id TEXT PRIMARY KEY,is_current INTEGER,list_order INTEGER,title TEXT,author TEXT,note_url TEXT,card_text TEXT,first_observed TEXT,last_observed TEXT,source_batch TEXT,source_batch_count INTEGER,full_text_collected INTEGER)')
    db.execute('CREATE TABLE IF NOT EXISTS metadata(name TEXT PRIMARY KEY,value TEXT)')
    db.execute('DELETE FROM notes')
    db.executemany('INSERT INTO notes VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', [tuple(r[f] if r[f] != '' or f != '目录序号_从1开始' else None for f in fields) for r in merged])
    db.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)', ('quality', json.dumps(quality, ensure_ascii=False)))
    db.commit()
    assert db.execute('SELECT COUNT(*) FROM notes').fetchone()[0] == len(merged)
    assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    db.close()
    with (OUT/'当前收藏.csv').open(encoding='utf-8-sig', newline='') as stream:
        assert len(list(csv.DictReader(stream))) == len(current_rows)
    shutil.copy2(ROOT/'收藏原始数据_197条.csv', OUT/'早期标题样本_197条.csv')
    shutil.copy2(ROOT/'收藏分析表_197条.csv', OUT/'早期样本主题标签_AI初分_待复核.csv')
    description = f'''# 小红书收藏数据集

采集日期：2026年10月28日（北京时间）。

本轮页面计数：{total}；本轮读取：{len(current_rows)}；历史补充：{len(historical)}；整合去重：{len(merged)}。

- 当前收藏.csv：本轮目录，一行一条笔记，按目录序号排列。UTF-8 BOM，可用 WPS 或 Excel 打开。
- 整合收藏.csv：当前目录与历史真实编号记录的并集。分析当前收藏时筛选“本轮是否出现 = 1”。
- 历史补充.csv：历史采集出现、本轮未出现的记录，不能直接认定为已删除或取消收藏。
- 收藏数据集.json / 收藏数据.sqlite：同一组整合记录及元数据；SQLite 主表为 notes，is_current = 1 表示本轮出现。
- 早期标题样本_197条.csv：早期样本包含缺少真实编号的条目，单独保留，不强行合并或重复计入总数。
- 早期样本主题标签_AI初分_待复核.csv：历史自动初分标签，不代表本人认同、性格或心理诊断。
- 质量检查.json：计数、缺口、重复、缺失字段及终点核对。
- 分析说明.md：基于已读部分的初步分析；关键词表与规则保留在同一文件夹，均待人工复核。
- 原始采集批次：本轮全部卡片批次及历史补充的对应批次，用于追溯记录，不要把重复出现次数当作用户行为频次。

## 字段与范围

笔记ID是唯一键；同标题不合并。目录序号只对应本轮排序；历史补充的当前序号为空。

本次读取的是收藏卡片中的标题、作者、链接、原始展示文字；未批量读取笔记正文、评论、图片或视频。

观察时间是采集时间，不是发布或收藏时间。部分早期观察没有时间戳，空值保留；时间戳有 Z 后缀时表示 UTC，北京时间加8小时。

标题空白保持为空，不补写。链接已移除认证查询参数；不含 Cookie、密码或订阅凭据。部分小红书链接打开时仍可能需要登录或在应用内搜索。

收藏内容只反映保存过的信息，不等于认同、亲身经历或已经采取行动，不能仅凭标题作心理诊断。

完整性以质量检查中的“本轮目录计数完全匹配”和“终点核对”为准；差额不会用虚构条目填充。
'''
    (OUT/'说明.md').write_text(description, encoding='utf-8')
    manifest = {p.relative_to(OUT).as_posix(): {'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in OUT.rglob('*') if p.is_file() and p.name != '文件校验.json'}
    (OUT/'文件校验.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    archive = ROOT/'小红书收藏数据集_20261028.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as zipped:
        for path in sorted(OUT.rglob('*')):
            if path.is_file():
                zipped.write(path, arcname=OUT.name+'/'+path.relative_to(OUT).as_posix())
    with zipfile.ZipFile(archive) as zipped:
        assert zipped.testzip() is None
    print(json.dumps({k:quality[k] for k in ['页面显示收藏数','本轮目录条数','历史补充条数','整合去重条数','本轮目录计数完全匹配','本轮空标题数','整合编号重复数']}, ensure_ascii=False))

if __name__ == '__main__':
    main()
