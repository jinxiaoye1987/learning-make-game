#!/usr/bin/env python3
"""从已生成的 site HTML 收回目录元数据，写成 catalog/survey.json。

只提取页面上已经公开的分类名、播放列表链接、集数、时长和标题。
不是字幕原文，也不会改写课程正文。分类总时长在原页面里按「小时/分」
显示，不满一小时才精确到秒；这里按页面上的显示值还原，供 site.py 再次
生成相同的总时长文案。单集时长按课时页上的分:秒读取。
"""
import html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
OUT = os.path.join(ROOT, "catalog", "survey.json")


def parse_clock(text):
    parts = [int(x) for x in text.strip().split(":")]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    raise ValueError(text)


def parse_total(text):
    hour = re.search(r"(\d+) 小时", text)
    minute = re.search(r"(\d+) 分", text)
    second = re.search(r"(\d+) 秒", text)
    if not minute:
        raise ValueError(text)
    total = int(minute.group(1)) * 60
    if hour:
        total += int(hour.group(1)) * 3600
    elif second:
        total += int(second.group(1))
    elif not hour:
        raise ValueError(text)
    return total


def main():
    home = open(os.path.join(SITE, "index.html"), encoding="utf-8").read()
    letters = re.findall(r'<span class="letter">([^<]+)</span>', home)
    categories = []
    for letter in letters:
        page = open(os.path.join(SITE, letter, "index.html"), encoding="utf-8").read()
        name = html.unescape(re.search(r'<h1>.*?<span class="note">([^<]*)</span>', page, re.S).group(1))
        done, total_eps = re.search(r"<b>(\d+)/(\d+)</b>已完成单集", page).groups()
        total_label = re.search(r"<b>([^<]+)</b>原视频总时长", page).group(1)
        url = re.search(r'<div class="stats">.*?<a href="(https://[^"]+)"', page, re.S).group(1)
        episodes = []
        for index_s, vid, clock, title_en in re.findall(
            r'href="(\d{2})-([^"]+)\.html".*?<span class="badge">([^<]+)</span>\s*<h3>.*?</h3><div class="note">([^<]*)</div>',
            page,
            re.S,
        ):
            episodes.append(
                {
                    "index": int(index_s),
                    "id": vid,
                    "title": html.unescape(title_en),
                    "duration": parse_clock(clock),
                    "url": f"https://youtu.be/{vid}",
                }
            )
        if len(episodes) != int(done) or int(done) != int(total_eps):
            raise SystemExit(f"{letter}: count mismatch {len(episodes)} {done}/{total_eps}")
        # 分类页只显示到分钟（满一小时时不显示秒）。用各集精确时长求和，
        # 才能让再次生成的分类页和首页总时长与现有页面一致。
        total_s = sum(ep["duration"] for ep in episodes)
        shown = parse_total(total_label)
        if abs(total_s - shown) >= 60:
            raise SystemExit(f"{letter}: duration drift {total_s} vs displayed {total_label}")
        categories.append(
            {
                "letter": letter,
                "name": name,
                "url": url,
                "episode_count": int(total_eps),
                "total_duration_s": total_s,
                "episodes": episodes,
            }
        )
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"categories": categories}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(
        "categories",
        len(categories),
        "episodes",
        sum(c["episode_count"] for c in categories),
        "wrote",
        OUT,
    )


if __name__ == "__main__":
    sys.exit(main())
