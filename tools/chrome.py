"""站点框架文案（页眉声明、页脚、关于页）。不包含课程正文。"""

INTRO = "我整理了这个游戏制作学习网站，方便回顾课程要点与自测。本站为非官方的个人学习总结。"
CHANNEL = "https://www.youtube.com/@sora_sakurai_en"
CHANNEL_NAME = "Masahiro Sakurai on Creating Games"
MAINTAINER = "https://github.com/jinxiaoye1987"
SITE_URL = "https://gamemap.speclab.info"

NAV = [
    ("index.html", "首页", "home"),
    ("index.html#cats", "全部分类", "cats"),
    ("map.html", "知识地图", "map"),
    ("quiz.html", "随机测验", "quiz"),
    ("search.html", "搜索", "search"),
    ("about.html", "关于", "about"),
]


def disclaimer_html(prefix):
    return (
        '<div class="disclaimer">非官方个人学习总结，未经权利人授权或背书，不能替代原视频。'
        "截图等第三方素材不因学习而获得使用许可。"
        f'<a href="{prefix}about.html">关于本站</a></div>'
    )


def footer_html(prefix):
    return (
        '<footer class="foot">'
        f"<p>{INTRO}</p>"
        f'<p>维护者 <a href="{MAINTAINER}">jinxiaoye1987</a>。本站与仓库有 AI 辅助整理与脚手架编写。'
        "课程观点来自原视频，由维护者整理，不能替代原视频。</p>"
        f'<p>本站不是樱井政博、任天堂、HAL 研究所、YouTube 频道「<a href="{CHANNEL}" target="_blank" rel="noopener">{CHANNEL_NAME}</a>」'
        "或其相关权利人的官方网站，未经上述权利人授权、审核或背书。</p>"
        "<p>内容依据公开视频整理，可能有偏差或遗漏。截图、字幕、游戏画面、作品名与角色形象等权利归各自权利人。"
        "学习这些笔记并不因此获得素材许可。</p>"
        f'<p><a href="{prefix}about.html">关于本站</a></p>'
        "</footer>"
    )


def about_body():
    return f'''<div class="wrap"><div class="hero-home"><h1>关于本站</h1>
<p>{INTRO}</p>
<p>维护者：<a href="{MAINTAINER}">jinxiaoye1987</a></p></div>
<section><h2>非官方声明</h2>
<ul class="points">
<li>本站不是樱井政博、任天堂、HAL 研究所、YouTube 频道「{CHANNEL_NAME}」或其相关权利人的官方网站。</li>
<li>未经上述权利人授权、审核或背书。</li>
<li>内容依据公开视频整理，可能有偏差或遗漏，不能替代原视频。</li>
<li>截图、字幕、游戏画面、作品名与角色形象等权利归各自权利人。</li>
<li>仅供学习参考。学习本站内容并不因此获得上述素材的使用许可。</li>
</ul>
<p>官方频道：<a href="{CHANNEL}" target="_blank" rel="noopener">{CHANNEL_NAME}</a></p></section>
<section><h2>AI 辅助</h2>
<p>本站及仓库有 AI 辅助整理与脚手架编写。课程观点来自原视频，由维护者整理，不能替代原视频。</p></section>
<section><h2>本站有什么</h2>
<p>现有 261 课时、15 个分类（A–N 与特别篇）和 795 道自测题。可以按分类浏览、搜索全文、查看知识地图，并在浏览器里做随机测验。记录只保存在本机浏览器中。</p></section>
<section><h2>图片与当前网站</h2>
<p>公开 Git 仓库可以不收录第三方截图和封面。课时页、分类页和首页里的图片路径仍然保留。用这份没有图片文件的快照打开页面时，这些图片会显示为缺失。这是仓库未收录文件，不是要求删掉原站图片，也不是要求改掉页面里的引用。</p>
<p>完整带图站点以另行保管的静态资源为准。只把这份无图目录上传为生产站点，页面会缺图，这不是正确的发布方式。</p>
<p>当前网站地址 <a href="{SITE_URL}">{SITE_URL}</a> 可能仍有访问保护，并不表示已经对所有访客公开。</p></section>
<section><h2>许可如何拆分</h2>
<p>维护者原创的脚本、样式、模板与布局代码见仓库中的 LICENSE。课程整理稿、测验、截图、封面、字幕、视频，以及 Mermaid 等第三方库，都不在该许可证的授权范围内，说明见仓库中的 NOTICE。</p></section>
</div>'''
