# MIT Admissions Blog Crawler

使用 Playwright 和 DrissionPage 抓取 MIT Admissions 博客，默认抓取前两页。

```powershell
py -m pip install -r requirements.txt
py crawl.py
```

输出文件：

- `blogs.csv`
- `playwright_blogs.csv`
- `drissionpage_blogs.csv`
- `raw_results.json`

可以用环境变量调整页数：

```powershell
$env:CRAWL_MAX_PAGES = "5"
py crawl.py
```
