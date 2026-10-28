import React, { useMemo, useState } from 'react';
import { DataComponent, DataTable, EvidenceChart, Filters, MetricCard, SectionHeader, SortableItem, SortableRegion, useDataApp } from '../../data-app-public.jsx';
import './favorites.css';

const themeSpec={type:'horizontalBar',x:'topic',y:'count',stackable:false,showXAxisLabel:false,showYAxisLabel:false,valueDecimals:0,colors:{count:'var(--chart-1)'},legend:{show:false}};
const coverageSpec={type:'horizontalStackedBar',x:'scope',y:'count',series:'status',showXAxisLabel:false,showYAxisLabel:false,valueDecimals:0,colors:{'本轮已读':'var(--chart-1)','尚未核实':'var(--chart-8)'}};

export function DashboardContent(){
  const {snapshot,queries,filters,setFilter,reviewedRows}=useDataApp();
  const [topic,setTopic]=useState('all');
  const [selected,setSelected]=useState(null);
  const notes=reviewedRows('notes',['noteId','state']);
  const allNotes=queries.notes.rows;
  const counts=useMemo(()=>{
    const found=new Map();
    notes.forEach(row=>row.topics.filter(t=>t!=='未命中规则').forEach(t=>found.set(t,(found.get(t)||0)+1)));
    return [...found].map(([topic,count])=>({topic,count})).sort((a,b)=>b.count-a.count||a.topic.localeCompare(b.topic));
  },[notes]);
  const topics=[...new Set(allNotes.flatMap(row=>row.topics))].sort();
  const tableRows=notes.filter(row=>topic==='all'||row.topics.includes(topic)).map(row=>({...row,topicText:row.topics.join(' · ')}));
  const unmatched=notes.filter(row=>row.topics.includes('未命中规则')).length;
  const coverage=queries.coverage.rows.map(row=>({...row,scope:'页面显示 920 条'}));
  const columns=[
    {key:'order',label:'序号',renderCell:value=>value??'—'},
    {key:'title',label:'标题',renderCell:(value,row)=><a className="favorite-note-link" href={row.url} target="_blank" rel="noopener noreferrer">{value}</a>},
    {key:'author',label:'作者'},
    {key:'topicText',label:'关键词主题'},
    {key:'state',label:'记录来源'},
  ];
  const rows=[
    {id:'favorites:totals',kind:'metrics',items:['favorites-visible','favorites-unmatched','favorites-history']},
    {id:'favorites:overview',items:['favorites-themes','favorites-coverage'],header:<SectionHeader id="favorites-overview-heading" title="收藏概览"/>},
    {id:'favorites:detail',items:['favorites-notes'],header:<SectionHeader id="favorites-detail-heading" title="看看具体收藏"/>},
  ];
  return <div className="favorites-page">
    <Filters sticky filters={snapshot.filters} queries={queries} values={filters} onChange={(id,value)=>{setFilter(id,value);setSelected(null);}}
      trailingControls={<span className="favorites-subtle">采集于 2026年10月28日</span>}/>
    <p className="favorites-scope" data-editable-id="favorites-scope-note" data-editable-narrative="true">本轮读取 631 / 920 条，另有 2 条历史补充。仍有 289 条未核实；本页展示收藏卡片，不含正文与图片。</p>
    <SortableRegion id="favorites:canvas" label="收藏图表" variant="canvas" spacing="standard" authoredRevision={1} columns={12} rows={rows}>
      <SortableItem id="favorites-visible" label="当前范围记录" kind="metric" span={4}>
        <MetricCard id="favorites-visible" queryId="notes" title="当前范围记录" value={String(notes.length)} sourceRows={notes} displayRows={[{指标:'当前范围记录',条数:notes.length}]} description="按真实笔记编号去重"/>
      </SortableItem>
      <SortableItem id="favorites-unmatched" label="未命中主题规则" kind="metric" span={4}>
        <MetricCard id="favorites-unmatched" queryId="notes" title="未命中主题规则" value={String(unmatched)} sourceRows={notes.filter(row=>row.topics.includes('未命中规则'))} displayRows={[{指标:'未命中主题规则',条数:unmatched}]} description="包含空标题或未被关键词覆盖的内容"/>
      </SortableItem>
      <SortableItem id="favorites-history" label="历史补充记录" kind="metric" span={4}>
        <MetricCard id="favorites-history" queryId="notes" title="历史补充记录（固定）" value="2" sourceRows={allNotes.filter(row=>row.state==='历史补充')} displayRows={[{指标:'历史补充记录',条数:2}]} description="此前读到，本轮目录未出现"/>
      </SortableItem>
      <SortableItem id="favorites-themes" label="标题中的主题" kind="chart" span={8} minSpan={5}>
        <EvidenceChart id="favorites-themes" queryId="notes" title="标题中的主题" variant="card" spec={themeSpec} rows={counts} sourceRows={notes} height={380}
          description="关键词初分，允许一条命中多个主题；各主题不可相加。"
          chartOptions={{getMarkActions:({row})=>[{label:'查看这些收藏',onSelect:()=>{setTopic(row.topic);setSelected(null);}}]}}>
          {!counts.length&&<p className="favorites-empty">当前范围没有命中主题的记录。</p>}
        </EvidenceChart>
      </SortableItem>
      <SortableItem id="favorites-coverage" label="本轮读取覆盖" kind="chart" span={4} minSpan={3}>
        <EvidenceChart id="favorites-coverage" queryId="coverage" title="本轮读取覆盖（固定）" variant="card" spec={coverageSpec} rows={coverage} sourceRows={queries.coverage.rows} height={180}>
          <div className="favorites-coverage-number" data-reviewed-rows="true"><strong>68.6<span>%</span></strong><p>631 条已读 · 289 条未核实</p></div>
          <p className="favorites-subtle">差额原因未确认，未读部分没有主题数据。覆盖率不包含历史补充。</p>
        </EvidenceChart>
      </SortableItem>
      <SortableItem id="favorites-notes" label="收藏明细" kind="table" span={12}>
        <DataComponent id="favorites-notes" queryId="notes" kind="table" title="收藏明细" variant="card" displayRows={tableRows} sourceRows={tableRows} description="可搜索标题、作者与主题；点击标题打开原笔记。">
          <div className="favorites-table-wrap">
            <DataTable label="收藏明细" rows={tableRows} columns={columns} rowKey="noteId" selectedRowKey={selected?.noteId}
              onRowSelect={row=>setSelected(row)} rowActionLabel={row=>'查看卡片原文：'+row.title}
              toolbarControls={<label className="favorites-topic-filter">主题<select aria-label="筛选收藏主题" value={topic} onChange={event=>{setTopic(event.target.value);setSelected(null);}}><option value="all">全部主题</option>{topics.map(t=><option key={t} value={t}>{t}</option>)}</select></label>}/>
          </div>
          {selected&&<aside className="favorites-note-detail" aria-label="卡片详情"><div><strong>{selected.title}</strong><button type="button" onClick={()=>setSelected(null)}>收起</button></div><p>{selected.cardText}</p></aside>}
        </DataComponent>
      </SortableItem>
    </SortableRegion>
    <p className="favorites-footer" data-editable-id="favorites-footnote" data-editable-narrative="true">主题是标题关键词线索，不是性格评分。收藏不等于认同，也不能说明实际经历；没有收藏时间，因此不绘制兴趣变化趋势。</p>
  </div>;
}
