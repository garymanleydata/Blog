import os
import shutil
import yaml
import markdown
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# Configuration
CONTENT_DIR = 'content'
POSTS_DIR = os.path.join(CONTENT_DIR, 'posts')
PAGES_DIR = os.path.join(CONTENT_DIR, 'pages')
TEMPLATE_DIR = 'templates'
STATIC_DIR = 'static'
OUTPUT_DIR = '_site'

def clean_output():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

def copy_static():
    shutil.copytree(STATIC_DIR, os.path.join(OUTPUT_DIR, 'static'))

def parse_markdown_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        meta = yaml.safe_load(parts[1])
        body = parts[2]
    else:
        meta = {}
        body = content
        
    html = markdown.markdown(body, extensions=['fenced_code', 'tables'])
    return meta, html

def slugify(text):
    return text.lower().replace(' ', '-').replace(/[^\w-]+/g, '')

def build_site():
    print("Starting build...")
    clean_output()
    copy_static()
    
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    
    # Load Posts
    posts = []
    categories = {}
    
    for filename in os.listdir(POSTS_DIR):
        if not filename.endswith('.md'):
            continue
            
        filepath = os.path.join(POSTS_DIR, filename)
        meta, html = parse_markdown_file(filepath)
        
        # Extract slug from filename (assuming YYYY-MM-DD-slug.md)
        slug = filename[11:-3] 
        meta['slug'] = slug
        meta['url'] = f"/articles/{slug}/"
        meta['html'] = html
        
        # Format date for display
        if 'date' in meta:
            if isinstance(meta['date'], str):
                meta['date_obj'] = datetime.strptime(meta['date'], '%Y-%m-%d')
            else:
                meta['date_obj'] = meta['date']
            meta['display_date'] = meta['date_obj'].strftime('%d %B %Y')
            
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
        html_out = article_template.render(post=post)
        with open(os.path.join(post_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_out)

    # Generate Homepage
    index_template = env.get_template('index.html')
    featured_posts = [p for p in posts if p.get('featured')]
    latest_posts = posts[:5]
    html_out = index_template.render(
        featured_posts=featured_posts, 
        latest_posts=latest_posts,
        categories=categories.keys()
    )
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_out)

    # Generate Main Articles List
    list_template = env.get_template('list.html')
    html_out = list_template.render(title="All Articles", posts=posts)
    articles_dir = os.path.join(OUTPUT_DIR, 'articles')
    os.makedirs(articles_dir, exist_ok=True)
    with open(os.path.join(articles_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_out)

    # Generate Category Pages
    category_template = env.get_template('category.html')
    for cat, cat_posts in categories.items():
        cat_slug = slugify(cat)
        # Sort category posts by date
        cat_posts.sort(key=lambda x: x.get('date_obj', datetime.min), reverse=True)
        cat_dir = os.path.join(OUTPUT_DIR, 'topics', cat_slug)
        os.makedirs(cat_dir, exist_ok=True)
        html_out = category_template.render(category=cat, posts=cat_posts)
        with open(os.path.join(cat_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_out)

    # Generate About Page
    about_path = os.path.join(PAGES_DIR, 'about.md')
    if os.path.exists(about_path):
        meta, html = parse_markdown_file(about_path)
        about_dir = os.path.join(OUTPUT_DIR, 'about')
        os.makedirs(about_dir, exist_ok=True)
        html_out = article_template.render(post={'title': 'About', 'html': html})
        with open(os.path.join(about_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_out)

    print(f"Build complete. {len(posts)} posts generated.")

if __name__ == '__main__':
    build_site()