# 我的收藏 / My Favorites

小红书收藏目录的数据备份与交互式可视化。包含主题分布、采集覆盖情况、主题筛选、标题与作者搜索，以及原笔记链接。

Personal Xiaohongshu favorites dataset and interactive dashboard, with keyword-based topics, coverage, filtering, search, and links to the original notes.

## 数据范围 / Coverage

采集日期：2026-10-28（北京时间）。

| 项目 / Measure | 条数 / Count |
| --- | ---: |
| 页面显示收藏 / Displayed favorites | 920 |
| 本轮已读取 / Captured in this pass | 631 |
| 历史补充 / Historical additions | 2 |
| 合并去重 / Merged unique note IDs | 633 |
| 本轮尚未核实 / Not verified in this pass | 289 |

本次采集未完成。631条为本轮网页连续读取的收藏卡片；2条历史补充此前出现、本轮未出现，不能直接认定为已删除或取消收藏。289条未核实的主题未知。正文、评论、图片和视频未批量下载。

Collection is incomplete. The 631 current records were captured from visible favorite cards. Two additional historical records were absent from the current pass; that does not establish deletion or unfavoriting. Another 289 displayed entries remain unverified. Full text, comments, images, and videos were not bulk downloaded.

主题是可复核的标题关键词初分，可重复命中多个主题，各主题数量不能相加。收藏不等于认同；分析不构成人格或心理诊断。观察时间不是发布或收藏时间。

Topics are reviewable keyword matches over card titles, with overlapping labels. Counts cannot be summed across topics. Saving a note does not imply endorsement; the interpretation is not a personality or mental-health diagnosis. Observation timestamps are not posting or saving timestamps.

## 文件 / Files

- `dashboard/src/content/dashboard/FavoritesDashboard.jsx`：可视化页面源码 / Authored dashboard UI.
- `dashboard/src/content/dashboard/favorites.css`：页面样式 / Authored styles.
- `dashboard/src/data.json`：图表使用的数据快照 / Reviewed dashboard snapshot.
- `dashboard/dist/`：已编译页面与对应数据文件 / Ready-to-serve build and its data sidecar.
- `data/当前收藏.csv`：631条本轮目录 / 631 current-pass records.
- `data/整合收藏.csv`：633条去重记录 / 633 merged unique records.
- `data/收藏数据集.json`、`data/收藏数据.sqlite`：同一数据的JSON与SQLite / JSON and SQLite equivalents.
- `data/主题关键词标记_待复核.csv`、`data/主题标记规则.json`：逐条标记与规则 / Per-note annotations and rules.
- `data/分析说明.md`：初步解释及证据限制 / Initial interpretation and evidence limits.
- `data/原始采集批次/`：原始卡片批次 / Original captured card batches.
- `analysis/`：采集之后使用的本地分析脚本快照 / Snapshots of local post-collection analysis scripts.

## 查看页面 / Run locally

安装Python 3后，在本仓库目录执行：

With Python 3 installed, run from this repository:

```sh
python serve_local.py
```

然后打开 / Then open: http://127.0.0.1:8000/

更换端口 / Choose another port:

```sh
python serve_local.py --port 8080
```

`dashboard/dist/index.html`与它对应的`dashboard/dist/snapshot.*.json`必须放在一起，通过本地HTTP服务打开。直接双击HTML可能无法读取数据文件。

Keep the HTML and its matching snapshot sidecar together and use the local HTTP server. Opening the HTML directly may prevent the snapshot from loading.

## 源码与重建 / Source and rebuilding

完整生成项目保存在`dashboard/`，其中的`AGENTS.md`说明原Data运行时的重建方式。当前项目包含经校验的编译结果，可以直接查看，不要求重新安装前端依赖。`analysis/`脚本保留原本地采集目录的相对路径假设；它们是分析记录，运行前需按脚本设置相应输入目录。

The generated project is retained under `dashboard/`; its `AGENTS.md` documents rebuilding with the original Data runtime. The verified build is included, so viewing it requires no frontend dependency installation. The scripts under `analysis/` retain their original input-directory assumptions and are reproducibility records; supply the expected inputs before rerunning them.

## 在线访问与更新 / Live website and updates

在线查看 / Open the dashboard: [我的收藏 / My Favorites](https://jutao402.github.io/xhs-favorites/)

网站由 GitHub Pages 托管，源码与数据保存在本仓库。仓库所有者已明确确认将这些个人收藏数据及分析公开。

The dashboard is hosted on GitHub Pages. Source code and data are preserved in this repository. The owner explicitly approved public sharing of these personal favorites data and analysis.

修改数据或页面源码后，先按 `dashboard/AGENTS.md` 重建，并将 `dashboard/dist/` 内的 HTML、对应数据文件和构建清单一同提交到 `main`。推送编译结果后会自动部署；仅修改源码不会自动重建页面。也可在 Actions 中手动运行 “Publish favorites dashboard”。发布脚本会校验文件哈希。

After changing data or UI source, rebuild using `dashboard/AGENTS.md` and commit the HTML, matching snapshot sidecar, and build manifest under `dashboard/dist/` together to `main`. Pushing the compiled build automatically deploys it; source-only changes do not rebuild the dashboard. You can also manually run “Publish favorites dashboard” in Actions. The deployment script verifies file hashes.
