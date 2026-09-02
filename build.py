import os
import shutil
import yaml
import markdown
import re
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from email.utils import format_datetime

# Configuration
CONTENT_DIR = 'content'
POSTS_DIR = os.path.join(CONTENT_DIR, 'posts')
PAGES_DIR = os.path.join(CONTENT_DIR, 'pages')
TEMPLATE_DIR = 'templates'
STATIC_DIR = 'static'
OUTPUT_DIR = '_site'
BASE_PATH = '/Blog'
SITE_URL = 'https://garymanleydata.github.io'  # Set to your GitHub Pages root domain

def clean_output():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

def copy_static():
    shutil.copytree(STATIC_DIR, os.path.join(OUTPUT_DIR, 'static'))

def calculate_reading_time(text, words_per_minute=200):
    words = len(re.findall(r'\w+', text))
    return max(1, round(words / words_per_minute))

def parse_markdown_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        meta = yaml.safe_load(parts[1]) or {}
        body = parts[2]
    else:
        meta = {}
        body = content
        
    html = markdown.markdown(body, extensions=['fenced_code', 'tables'])
    meta['reading_time'] = calculate_reading_time(body)
    return meta, html

def slugify(text):
    text = text.lower().replace(' ', '-')
    return re.sub(r'[^\w\-]', '', text)

def build_site():
    print("Starting build...")
    clean_output()
    copy_static()
    
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    
    posts = []
    categories = {}
    sitemap_pages = []
    
    # Track home and main listings in sitemap
    sitemap_pages.append({'url': f"{BASE_PATH}/", 'lastmod': datetime.today().strftime('%Y-%m-%d')})
    sitemap_pages.append({'url': f"{BASE_PATH}/articles/", 'lastmod': datetime.today().strftime('%Y-%m-%d')})

    # Load Posts
    if os.path.exists(POSTS_DIR):
        for filename in os.listdir(POSTS_DIR):
            if not filename.endswith('.md'):
                continue
                
            filepath = os.path.join(POSTS_DIR, filename)
            meta, html = parse_markdown_file(filepath)
            
            slug = filename[11:-3] 
            meta['slug'] = slug
            meta['url'] = f"{BASE_PATH}/articles/{slug}/"
            meta['html'] = html
            
            # Format dates
            if 'date' in meta:
                if isinstance(meta['date'], str):
                    meta['date_obj'] = datetime.strptime(meta['date'], '%Y-%m-%d')
                else:
                    meta['date_obj'] = meta['date']
                meta['display_date'] = meta['date_obj'].strftime('%d %B %Y')
                meta['rss_date'] = format_datetime(datetime.combine(meta['date_obj'], datetime.min.time()))
                meta['iso_date'] = meta['date_obj'].strftime('%Y-%m-%d')
            else:
                meta['date_obj'] = datetime.min
                meta['display_date'] = ''
                meta['rss_date'] = ''
                meta['iso_date'] = ''
                
            posts.append(meta)
            
            # Aggregate categories
            category = meta.get('category', 'Uncategorised')
            if category not in categories:
                categories[category] = []
            categories[category].append(meta)

    # Sort posts by date descending
    posts.sort(key=lambda x: x.get('date_obj', datetime.min), reverse=True)
    
    # Generate Article Pages
    article_template = env.get_template('article.html')
    for post in posts:
        post_dir = os.path.join(OUTPUT_DIR, 'articles', post['slug'])
        os.makedirs(post_dir, exist_ok=True)
        html_out = article_template.render(post=post, base_path=BASE_PATH)
        with open(os.path.join(post_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_out)
        sitemap_pages.append({'url': post['url'], 'lastmod': post.get('iso_date')})

    # Generate Homepage
    index_template = env.get_template('index.html')
    featured_posts = [p for p in posts if p.get('featured')]
    latest_posts = posts[:5]
    html_out = index_template.render(
        featured_posts=featured_posts, 
        latest_posts=latest_posts,
        categories=categories.keys(),
        base_path=BASE_PATH
    )
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_out)

    # Generate Main Articles List
    list_template = env.get_template('list.html')
    html_out = list_template.render(title="All Articles", posts=posts, base_path=BASE_PATH)
    articles_dir = os.path.join(OUTPUT_DIR, 'articles')
    os.makedirs(articles_dir, exist_ok=True)
    with open(os.path.join(articles_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_out)

    # Generate Category Pages
    category_template = env.get_template('category.html')
    for cat, cat_posts in categories.items():
        cat_slug = slugify(cat)
        cat_posts.sort(key=lambda x: x.get('date_obj', datetime.min), reverse=True)
        cat_dir = os.path.join(OUTPUT_DIR, 'topics', cat_slug)
        os.makedirs(cat_dir, exist_ok=True)
        html_out = category_template.render(category=cat, posts=cat_posts, base_path=BASE_PATH)
        with open(os.path.join(cat_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_out)
        sitemap_pages.append({'url': f"{BASE_PATH}/topics/{cat_slug}/", 'lastmod': datetime.today().strftime('%Y-%m-%d')})

    # Generate About Page
    about_path = os.path.join(PAGES_DIR, 'about.md')
    if os.path.exists(about_path):
        meta, html = parse_markdown_file(about_path)
        about_dir = os.path.join(OUTPUT_DIR, 'about')
        os.makedirs(about_dir, exist_ok=True)
        html_out = article_template.render(post={'title': 'About', 'html': html}, base_path=BASE_PATH)
        with open(os.path.join(about_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_out)
        sitemap_pages.append({'url': f"{BASE_PATH}/about/", 'lastmod': datetime.today().strftime('%Y-%m-%d')})

    # Generate RSS Feed
    rss_template = env.get_template('rss.xml')
    rss_out = rss_template.render(
        posts=posts[:20],
        site_url=SITE_URL,
        base_path=BASE_PATH
    )
    with open(os.path.join(OUTPUT_DIR, 'rss.xml'), 'w', encoding='utf-8') as f:
        f.write(rss_out)

    # Generate Sitemap
    sitemap_template = env.get_template('sitemap.xml')
    sitemap_out = sitemap_template.render(
        pages=sitemap_pages,
        site_url=SITE_URL
    )
    with open(os.path.join(OUTPUT_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(sitemap_out)

    print(f"Build complete. Generated {len(posts)} posts, rss.xml, and sitemap.xml.")

if __name__ == '__main__':
    build_site()