import csv
import json
import os
import re
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup
from DrissionPage import ChromiumOptions, ChromiumPage
from playwright.sync_api import sync_playwright

base_url = "https://mitadmissions.org/blogs/"
max_pages = int(os.getenv("CRAWL_MAX_PAGES", "3"))
# 第一页没有 page/1，后续页面使用 /page/2/、/page/3/。
page_urls = [base_url] + [f"{base_url}page/{number}/" for number in range(2, max_pages + 1)]
fields = ["Title", "Author", "Comment Count", "Time", "Article Content", "Images In Article"]

# Playwright 用于抓取列表页，并进入文章详情页获取正文和正文图片。
playwright_rows = []
playwright_seen = set()

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    )
    list_page = browser.new_page()
    detail_page = browser.new_page()

    for page_url in page_urls:
        print(f"Playwright 正在抓取：{page_url}", flush=True)
        list_page.goto(page_url, wait_until="domcontentloaded", timeout=60000)
        list_page.wait_for_timeout(1000)
        soup = BeautifulSoup(list_page.content(), "html.parser")
        cards = soup.select("div.tease__inner")
        if not cards:
            break

        for card in cards:
            title = card.select_one("span.post-tease__title")
            link = card.select_one("a.post-tease__h__link")
            author = card.select_one("li.post-tease__meta-item--author a")
            date = card.select_one("li.tease__meta-item--date")
            comments = card.select_one("li.tease__meta-item--comments a")
            article_url = link.get("href", "") if link else ""

            if not title or not article_url or article_url in playwright_seen:
                continue
            playwright_seen.add(article_url)

            # 进入详情页抓取正文和文章图片。
            detail_page.goto(article_url, wait_until="domcontentloaded", timeout=60000)
            detail_soup = BeautifulSoup(detail_page.content(), "html.parser")
            body = detail_soup.select_one("div.article__body")
            images = []
            content = ""

            if body:
                content = body.get_text(" ", strip=True)
                images = [
                    image.get("src") or image.get("data-src")
                    for image in body.select("img")
                    if image.get("src") or image.get("data-src")
                ]

            comment_text = comments.get_text(" ", strip=True) if comments else ""
            comment_count = re.search(r"\d+", comment_text)

            playwright_rows.append({
                "Title": title.get_text(" ", strip=True),
                "Author": author.get_text(" ", strip=True) if author else "",
                "Comment Count": comment_count.group() if comment_count else "0",
                "Time": date.get_text(" ", strip=True) if date else "",
                "Article Content": content,
                "Images In Article": " | ".join(dict.fromkeys(images)),
            })

        print(f"Playwright 已完成 {len(playwright_rows)} 篇", flush=True)

    browser.close()

# DrissionPage 单独抓取相同内容。
drission_rows = []
drission_seen = set()
options = ChromiumOptions().headless(True)
page = ChromiumPage(addr_or_opts=options)

for page_url in page_urls:
    page.get(page_url)
    soup = BeautifulSoup(page.html, "html.parser")
    cards = soup.select("div.tease__inner")
    if not cards:
        break

    for card in cards:
        title = card.select_one("span.post-tease__title")
        link = card.select_one("a.post-tease__h__link")
        author = card.select_one("li.post-tease__meta-item--author a")
        date = card.select_one("li.tease__meta-item--date")
        comments = card.select_one("li.tease__meta-item--comments a")
        article_url = link.get("href", "") if link else ""

        if not title or not article_url or article_url in drission_seen:
            continue
        drission_seen.add(article_url)

        comment_text = comments.get_text(" ", strip=True) if comments else ""
        comment_count = re.search(r"\d+", comment_text)

        page.get(article_url)
        detail_soup = BeautifulSoup(page.html, "html.parser")
        body = detail_soup.select_one("div.article__body")
        content = body.get_text(" ", strip=True) if body else ""
        images = []
        if body:
            images = [
                image.get("src") or image.get("data-src")
                for image in body.select("img")
                if image.get("src") or image.get("data-src")
            ]

        drission_rows.append({
            "Title": title.get_text(" ", strip=True),
            "Author": author.get_text(" ", strip=True) if author else "",
            "Comment Count": comment_count.group() if comment_count else "0",
            "Time": date.get_text(" ", strip=True) if date else "",
            "Article Content": content,
            "Images In Article": " | ".join(dict.fromkeys(images)),
        })

        print(f"DrissionPage 已完成 {len(drission_rows)} 篇：{title.get_text(' ', strip=True)}", flush=True)

page.quit()

# CSV 使用包含完整正文的 Playwright 结果；两种结果同时保存到 JSON。
results = {"playwright": playwright_rows, "drissionpage": drission_rows}
rows = playwright_rows or drission_rows
output_dir = Path(__file__).resolve().parent
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for file_name, data in (
    ("blogs.csv", rows),
    ("playwright_blogs.csv", playwright_rows),
    ("drissionpage_blogs.csv", drission_rows),
):
    output_file = output_dir / file_name
    try:
        file = output_file.open("w", newline="", encoding="utf-8-sig")
    except PermissionError:
        output_file = output_dir / f"{output_file.stem}_{timestamp}.csv"
        file = output_file.open("w", newline="", encoding="utf-8-sig")

    with file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)
    print(f"已保存 {len(data)} 条：{output_file}", flush=True)

(output_dir / "raw_results.json").write_text(
    json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
)
