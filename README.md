# 樱井政博游戏制作课程 · 非官方中文学习笔记

我整理了这个游戏制作学习网站，方便回顾课程要点与自测。本站为非官方的个人学习总结。

维护者：[jinxiaoye1987](https://github.com/jinxiaoye1987)

本站及仓库有 AI 辅助整理与脚手架编写。课程观点来自原视频，由维护者整理，不能替代原视频。

官方频道：[Masahiro Sakurai on Creating Games](https://www.youtube.com/@sora_sakurai_en)

## 这是什么

这是把上述 YouTube 频道逐集整理成的中文图文学习站，纯静态 HTML、CSS 和 JavaScript。可以按分类阅读、搜索、查看知识地图，并做随机测验。

## 非官方声明

- 本站不是樱井政博、任天堂、HAL 研究所、该 YouTube 频道或其相关权利人的官方网站。
- 未经上述权利人授权、审核或背书。
- 内容依据公开视频整理，可能有偏差或遗漏，不能替代原视频。
- 截图、字幕、游戏画面、作品名与角色形象等权利归各自权利人。
- 仅供学习参考。学习这些笔记并不因此获得素材许可。

## 功能概览

| 项目 | 数量 |
|---|---|
| 课时 | 261 |
| 分类 | 15（A–N，以及特别篇） |
| 自测题 | 795 |

分类包括工作态度、游戏本质、企划与游戏设计、设计细节、团队管理、图形美术、动画、特效、音频、UI、程序与技术、市场营销、杂谈、游戏概念和特别篇。首页、分类页、知识地图、搜索和随机测验都在 `site/` 中。

## 目录

```text
README.md                 本说明
LICENSE                   只覆盖维护者原创代码
NOTICE                    第三方库与课程素材边界
CONTRIBUTING.md           怎样提交勘误和程序改进
CODE_OF_CONDUCT.md        行为准则
SECURITY.md               漏洞报告方式
docs/DEPLOY-CLOUDFLARE.md 部署说明（本文档不执行部署）
site/                     可直接预览的静态站点，含相对路径图片
content/                  课时整理稿（正文、元数据、题目）
specs/                    238 份课次规格；A 类 23 课不在这里
catalog/survey.json       从现有页面收回的目录元数据
tools/                    生成与检查脚本
third_party/mermaid/      Mermaid 11.17.2 与上游许可证
.github/                  Issue、拉取请求模板与无凭证检查
```

## 本地预览

不需要构建。在仓库根目录执行：

```bash
python3 -m http.server 8765 --directory site
```

然后打开 <http://127.0.0.1:8765/> 。首页、知识地图、搜索和随机测验都可以在本地使用。搜索和测验的数据已经放进 `site/data/*.js`，用本地文件打开时也不依赖远程接口。封面和截图也在 `site/` 里，用相对路径加载。

## 构建

已发布的 `site/` 就是当前页面。需要从整理稿重新生成时：

```bash
python3 tools/extract_catalog.py
python3 tools/site.py --root .
```

`tools/site.py` 默认使用本仓库根目录，读取 `content/` 和 `catalog/survey.json`，并会替换整个输出目录。Mermaid 从 `third_party/mermaid/mermaid.min.js` 复制到站点。图片文件只会从 `content/` 里实际存在的文件复制过去；当前这些截图和封面放在 `site/`，不在 `content/`。因此不要对现有的 `site/` 直接重跑生成，否则图片文件会被清掉，只留下引用。需要试跑时请把 `--site` 指到别的目录。

早先的脚本写着本机绝对路径 `/workspace/yt-lesson`。`site.py` 已改为可用 `--root` 指定目录。`fetch.sh`、`prep.sh`、`mkimg.sh` 等仍指向那棵本机树，它们依赖 `eps/` 里的视频和字幕缓存。

这些下载和预处理脚本是历史维护工具。已知至少有部分 `video.mp4` 和日语自动字幕缺失或为空，YouTube 或 yt-dlp 还可能被限流。它们不能保证把缺失的原始源数据全部重新下载，也不是对公众的一键复原。

重新生成不会改写 `content/` 里的课程正文。可发布的完整站点就是仓库里的 `site/` 目录，其中已经包含被引用的图片。

## 图片

截图和封面以相对路径放在 `site/{分类}/img/{视频id}/`，和 HTML、CSS、JS 在同一棵静态目录里。之后用 Cloudflare Pages 发布时，上传这个完整目录即可，图片与页面同一包，不使用 R2、Cloudflare Images 或其他单独的图片服务。

仓库里现有 3262 个图片文件，对应页面中 3538 处带 `src` 的引用（封面在首页、分类页和课时页重复引用）。静态检查要求这些引用都能在仓库里找到文件。缺图会失败，也不要靠删除 `img` 来让检查变绿。

把图片放进本仓库不表示权利人再授权。它们不适用根目录的 MIT 许可证。详见 `NOTICE`。

## 许可

根目录 `LICENSE` 是 MIT，只覆盖维护者原创的脚本、样式、模板和布局代码。

课程整理稿、测验、截图、封面、字幕、视频，以及 Mermaid，都不在该许可证里。Mermaid 11.17.2 的上游许可证文本在 `third_party/mermaid/LICENSE`。其余边界在 `NOTICE`。

## 贡献

看 [CONTRIBUTING.md](CONTRIBUTING.md)。程序问题与课程勘误使用不同的 Issue 模板。漏洞请按 [SECURITY.md](SECURITY.md) 走 GitHub 私密报告，不要发到公开 Issue。

本地检查：

```bash
python3 tools/check_public_site.py
```

GitHub Actions 在拉取请求和推送时运行同一项检查，不配置密钥，也不访问 YouTube。

## 当前网站

<https://gamemap.speclab.info>

该地址可能仍有访问保护，并不表示已经对所有访客公开。部署到现有 Cloudflare Pages 项目 `gamemap-sakurai` 的步骤见 [docs/DEPLOY-CLOUDFLARE.md](docs/DEPLOY-CLOUDFLARE.md)。不要修改 Cloudflare Access。本仓库不包含部署用的令牌。
