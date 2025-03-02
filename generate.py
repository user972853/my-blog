import os
import json
import markdown
import yaml
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# مسیرهای اصلی
CONTENT_DIR = "content/posts"
BUILD_DIR = "build"
POSTS_BUILD_DIR = os.path.join(BUILD_DIR, "posts")
CATEGORIES_BUILD_DIR = os.path.join(BUILD_DIR, "categories")
TEMPLATES_DIR = "templates"
DATA_DIR = "data"

# ایجاد پوشه‌های مورد نیاز در خروجی
os.makedirs(BUILD_DIR, exist_ok=True)
os.makedirs(POSTS_BUILD_DIR, exist_ok=True)
os.makedirs(CATEGORIES_BUILD_DIR, exist_ok=True)

# بارگذاری تنظیمات سایت
with open(os.path.join(DATA_DIR, "config.json"), "r", encoding="utf-8") as f:
    config = json.load(f)

# راه‌اندازی محیط Jinja2
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
post_template = env.get_template("post.html")
index_template = env.get_template("index.html")
category_template = env.get_template("category.html")  # قالب صفحه دسته‌بندی

posts_list = []

# تابع برای خواندن front-matter از فایل Markdown
def parse_markdown(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if content.startswith("---"):
        # جدا کردن front-matter
        parts = content.split("---", 2)
        if len(parts) >= 3:
            front_matter = yaml.safe_load(parts[1])
            md_content = parts[2]
            return front_matter, md_content
    return {}, content

# پردازش فایل‌های Markdown
for filename in os.listdir(CONTENT_DIR):
    if filename.endswith(".md"):
        filepath = os.path.join(CONTENT_DIR, filename)
        front_matter, md_content = parse_markdown(filepath)
        
        # تبدیل Markdown به HTML
        html_content = markdown.markdown(md_content, extensions=["extra"])
        
        # گرفتن عنوان از front-matter یا از نام فایل
        post_title = front_matter.get("title")
        if not post_title:
            post_title = filename.replace(".md", "").replace("-", " ").title()
        
        # گرفتن دسته‌بندی، پیش‌فرض "سایر"
        post_category = front_matter.get("category", "سایر")
        
        # سایر تنظیمات سفارشی مثل پس‌زمینه
        post_background = front_matter.get("background", None)
        
        # زمان ایجاد یا تغییر فایل (برای ترتیب نمایش)
        file_timestamp = os.path.getmtime(filepath)
        post_date = datetime.fromtimestamp(file_timestamp).strftime("%Y-%m-%d %H:%M:%S")
        
        # آماده‌سازی context برای قالب پست
        post_context = {
            "base_url": config.get("base_url", "/"),
            "site_title": config.get("site_title", "وبلاگ من"),
            "menu": config.get("menu", []),
            "author": config.get("author", "ناشناس"),
            "post_title": post_title,
            "post_date": post_date,
            "post_content": html_content,
            "post_background": post_background,
            "category": post_category
        }
        
        # تولید خروجی HTML برای پست
        rendered_post = post_template.render(**post_context)
        
        # نام فایل خروجی بر اساس زمان یا نام فایل (برای یکتایی)
        output_filename = filename.replace(".md", ".html")
        output_filepath = os.path.join(POSTS_BUILD_DIR, output_filename)
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(rendered_post)
        
        posts_list.append({
            "title": post_title,
            "date": post_date,
            "mtime": file_timestamp,
            "url": f"posts/{output_filename}",
            "category": post_category
        })

# مرتب‌سازی پست‌ها بر اساس زمان تغییر فایل به ترتیب صعودی (ایجاد شدن)
posts_list.sort(key=lambda x: x["mtime"])

# تولید صفحه اصلی
index_context = {
    "base_url": config.get("base_url", "/"),
    "site_title": config.get("site_title", "وبلاگ من"),
    "menu": config.get("menu", []),
    "author": config.get("author", "ناشناس"),
    "posts": posts_list
}
rendered_index = index_template.render(**index_context)
with open(os.path.join(BUILD_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(rendered_index)

# گروه‌بندی پست‌ها بر اساس دسته‌بندی
categories = {}
for post in posts_list:
    cat = post["category"]
    categories.setdefault(cat, []).append(post)

# تولید صفحات دسته‌بندی
for cat, posts in categories.items():
    context = {
        "base_url": config.get("base_url", "/"),
        "site_title": config.get("site_title", "وبلاگ من"),
        "menu": config.get("menu", []),
        "author": config.get("author", "ناشناس"),
        "category": cat,
        "posts": posts
    }
    rendered_category = category_template.render(**context)
    # برای نام فایل دسته‌بندی (حروف فارسی ممکنه نیاز به URL-encoding داشته باشد)
    filename_cat = f"{cat}.html"
    with open(os.path.join(CATEGORIES_BUILD_DIR, filename_cat), "w", encoding="utf-8") as f:
        f.write(rendered_category)

print("Build complete! Check the 'build' folder for generated HTML files.")
