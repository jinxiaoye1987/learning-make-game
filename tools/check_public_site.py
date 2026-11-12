#!/usr/bin/env python3
"""公开仓库的静态检查。

核对课时、题目、相对链接和声明是否还在。
第三方图片未纳入本仓库时只报告缺失，不视为失败，也不会改动 HTML。
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import chrome

SITE = os.path.join(ROOT, "site")
EXPECTED_LESSONS = {
    "A": 23, "B": 29, "C": 30, "D": 18, "E": 15, "F": 20, "G": 18,
    "H": 11, "I": 14, "J": 15, "K": 9, "L": 9, "M": 31, "N": 13, "extra": 6,
}
MIN_IMG_SRC = 3538
MERMAID_SHA = "581ed7d74bd9048d0e3a91363927d72ef22942d7722546b27f7cc29e35390eb8"
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".avif"}
FORBIDDEN_NAME = {"ja.txt", "en_ocr.txt", "handoff-notes.txt"}
FORBIDDEN_EXT = {".mp4", ".vtt", ".log"}
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
SECRET_RE = re.compile(r"BEGIN (?:RSA |OPENSSH )?PRIVATE KEY|AKIA[0-9A-Z]{16}|xox[baprs]-")

failures = []


def fail(msg):
    failures.append(msg)


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def lesson_pages():
    found = []
    for letter in EXPECTED_LESSONS:
        folder = os.path.join(SITE, letter)
        if not os.path.isdir(folder):
            fail(f"缺少分类目录 site/{letter}")
            continue
        pages = [fn for fn in os.listdir(folder) if re.fullmatch(r"\d{2}-.+\.html", fn)]
        found.append((letter, pages))
    return found


def check_counts():
    pages = lesson_pages()
    total = 0
    for letter, names in pages:
        total += len(names)
        if len(names) != EXPECTED_LESSONS[letter]:
            fail(f"site/{letter} 课时页 {len(names)}，期望 {EXPECTED_LESSONS[letter]}")
        for fn in names:
            text = open(os.path.join(SITE, letter, fn), encoding="utf-8").read()
            if "cover.jpg" not in text:
                fail(f"site/{letter}/{fn} 缺少封面图片引用")
    if total != 261:
        fail(f"课时页合计 {total}，期望 261")
    content_ids = set()
    quiz_n = 0
    for letter in EXPECTED_LESSONS:
        base = os.path.join(ROOT, "content", letter)
        if not os.path.isdir(base):
            fail(f"缺少 content/{letter}")
            continue
        for vid in os.listdir(base):
            d = os.path.join(base, vid)
            if not os.path.isdir(d):
                continue
            content_ids.add((letter, vid))
            quiz_path = os.path.join(d, "quiz.json")
            if not os.path.exists(quiz_path):
                fail(f"缺少 {os.path.relpath(quiz_path, ROOT)}")
                continue
            quiz_n += len(json.load(open(quiz_path, encoding="utf-8")))
    if len(content_ids) != 261:
        fail(f"content 课时目录 {len(content_ids)}，期望 261")
    if quiz_n != 795:
        fail(f"content 题目 {quiz_n}，期望 795")
    bank = json.load(open(os.path.join(SITE, "data", "quiz.json"), encoding="utf-8"))
    if len(bank) != 795:
        fail(f"site/data/quiz.json 题目 {len(bank)}，期望 795")
    index = json.load(open(os.path.join(SITE, "data", "search-index.json"), encoding="utf-8"))
    if len(index) != 1558:
        fail(f"搜索索引 {len(index)} 条，期望 1558")
    for name in ("index.html", "map.html", "search.html", "quiz.html", "about.html"):
        if not os.path.exists(os.path.join(SITE, name)):
            fail(f"缺少 site/{name}")


def check_links_and_images():
    img_src = 0
    missing_images = []
    checked = 0
    attr = re.compile(r"""(?:src|href|action)\s*=\s*["']([^"']+)["']""", re.I)
    for dirpath, _, names in os.walk(SITE):
        for fn in names:
            if not fn.endswith((".html", ".css", ".js")):
                continue
            if fn == "mermaid.min.js":
                continue
            path = os.path.join(dirpath, fn)
            text = open(path, encoding="utf-8", errors="ignore").read()
            if fn.endswith(".html"):
                if chrome.INTRO not in text:
                    fail(f"{os.path.relpath(path, ROOT)} 缺少指定的个人介绍")
                if 'class="disclaimer"' not in text:
                    fail(f"{os.path.relpath(path, ROOT)} 缺少全站声明")
                img_src += len(re.findall(r'<img\b[^>]*\bsrc="[^"]+"', text))
            for raw in attr.findall(text):
                if raw.startswith(("http://", "https://", "javascript:", "data:")) or raw.startswith("mail" + "to:"):
                    continue
                if any(tok in raw for tok in ("'+", "${", "\\")):
                    continue
                url = raw.split("#", 1)[0].split("?", 1)[0]
                if not url:
                    continue
                checked += 1
                ext = os.path.splitext(url)[1].lower()
                target = os.path.normpath(os.path.join(dirpath, url))
                if os.path.exists(target):
                    continue
                rel = os.path.relpath(path, SITE)
                if ext in IMAGE_EXT:
                    missing_images.append((rel, url))
                else:
                    fail(f"缺少站内文件 {rel} -> {url}")
    if img_src < MIN_IMG_SRC:
        fail(f"带 src 的 img 只有 {img_src} 个，少于 {MIN_IMG_SRC}。不要删除图片引用。")
    print(f"relative links checked: {checked}")
    print(f"img src attributes: {img_src}")
    print(
        "optional third-party images missing: "
        f"{len(missing_images)} references "
        "(expected in this snapshot; not a failure; references were kept)"
    )
    if missing_images:
        print("production note: do not deploy this image-free snapshot")


def check_secrets_and_forbidden():
    for dirpath, dirnames, names in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__", ".wrangler"}]
        for fn in names:
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, ROOT)
            lower = fn.lower()
            ext = os.path.splitext(fn)[1].lower()
            if lower in FORBIDDEN_NAME or ext in FORBIDDEN_EXT or fn.startswith("creating-games-zh"):
                fail(f"不应入库的文件 {rel}")
            if fn.endswith((".min.js",)) and os.path.getsize(path) > 1_000_000:
                continue
            try:
                text = open(path, encoding="utf-8").read()
            except (UnicodeDecodeError, IsADirectoryError):
                continue
            if "mail" + "to:" in text.lower():
                fail(f"出现邮件链接 {rel}")
            emails = [e for e in EMAIL_RE.findall(text) if not e.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".js", ".css"))]
            if emails:
                fail(f"出现邮箱样式字符串 {rel}（共 {len(emails)} 处，值不在此输出）")
            if SECRET_RE.search(text):
                fail(f"出现疑似凭证 {rel}")
    workflow = os.path.join(ROOT, ".github", "workflows", "static-check.yml")
    if not os.path.exists(workflow):
        fail("缺少 .github/workflows/static-check.yml")
    else:
        wf = open(workflow, encoding="utf-8").read()
        if "pull_request" not in wf or "push" not in wf:
            fail("静态检查工作流需要在 pull_request 与 push 上运行")
        if "secrets." in wf or "CLOUDFLARE_API_TOKEN" in wf:
            fail("CI 工作流不应引用密钥或 Cloudflare token")


def check_mermaid():
    copies = [
        os.path.join(ROOT, "third_party", "mermaid", "mermaid.min.js"),
        os.path.join(SITE, "assets", "vendor", "mermaid.min.js"),
    ]
    for path in copies:
        if not os.path.exists(path):
            fail(f"缺少 {os.path.relpath(path, ROOT)}")
            continue
        digest = sha256(path)
        if digest != MERMAID_SHA:
            fail(f"{os.path.relpath(path, ROOT)} 哈希与 mermaid 11.17.2 不一致")
    license_path = os.path.join(ROOT, "third_party", "mermaid", "LICENSE")
    if not os.path.exists(license_path):
        fail("缺少 third_party/mermaid/LICENSE")
    else:
        head = open(license_path, encoding="utf-8").read(80)
        if "The MIT License (MIT)" not in head:
            fail("mermaid LICENSE 不是已核对的上游文本开头")


def main():
    check_counts()
    check_links_and_images()
    check_secrets_and_forbidden()
    check_mermaid()
    if failures:
        print(f"FAILED {len(failures)}")
        for item in failures:
            print(" -", item)
        return 1
    print("static check passed")
    print("261 lessons, 795 quiz items, image references retained")
    return 0


if __name__ == "__main__":
    sys.exit(main())
