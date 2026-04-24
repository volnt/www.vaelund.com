#!/usr/bin/env python3
"""
Vaelund Devlog Generator
Reads _posts/*.md, generates devlog/index.html and devlog/<slug>.html
Run manually after adding a new post.

Tone guide: Factorio-inspired:
- Direct, honest, no corporate filler
- Short sentences. Lists of concrete things done.
- Admit what broke, what took too long, what didn't work
- Technical detail where it matters
- No hype. No "we're excited to". Just what happened.
"""

import re
import os
import sys
from datetime import datetime

POSTS_DIR = "_posts"
OUTPUT_INDEX = "devlog/index.html"
OUTPUT_DIR = "devlog"
BASE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} -- Vaelund Devlog</title>
  <link rel="stylesheet" href="/static/css/devlog.css">
  <link rel="icon" type="image/png" href="/favicon.png">
</head>
<body>
  <nav class="devlog-nav">
    <a href="/#devlog" class="back-link">← Back to site</a>
    <a href="/" class="site-link">Vaelund</a>
  </nav>
  <main class="devlog-post">
    <header class="post-header">
      <div class="post-meta">
        <span class="post-date">{date}</span>
        <span class="post-tag">{tag}</span>
      </div>
      <h1 class="post-title">{title}</h1>
    </header>
    <div class="post-body">
{content}
    </div>
    <footer class="post-footer">
      <a href="/devlog/" class="back-link">← Back to Devlog</a>
    </footer>
  </main>
</body>
</html>
"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Devlog -- Vaelund</title>
  <link rel="stylesheet" href="/static/css/devlog.css">
  <link rel="icon" type="image/png" href="/favicon.png">
</head>
<body>
  <nav class="devlog-nav">
    <a href="/" class="site-link">← Vaelund</a>
  </nav>
  <main class="devlog-index">
    <header class="index-header">
      <h1>Devlog</h1>
      <p>Progress on Vaelund, one week at a time.</p>
    </header>
    <div class="post-list">
{posts}
    </div>
  </main>
</body>
</html>
"""

POST_LINK_TEMPLATE = """      <article class="post-card">
        <div class="post-meta">
          <span class="post-date">{date}</span>
          <span class="post-tag">{tag}</span>
        </div>
        <h2 class="post-title"><a href="/devlog/{slug}">{title}</a></h2>
        <p class="post-excerpt">{excerpt}</p>
        <a href="/devlog/{slug}" class="read-more">Read more →</a>
      </article>
"""


def parse_frontmatter(content):
    """Parse YAML-like frontmatter from a markdown file."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if not match:
        return {}, content
    fm_text, body = match.groups()
    fm = {}
    for line in fm_text.splitlines():
        if ':' in line:
            key, val = line.split(':', 1)
            fm[key.strip()] = val.strip().strip('"').strip("'")
    return fm, body


def slugify(text):
    """Convert a title to a URL slug."""
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def basic_markdown(text):
    """
    Simple markdown-to-HTML converter.
    Handles: h1-h3, h2, p, **bold**, *italic*, `code`, ```code blocks```,
    - lists, [links](url), blockquotes.
    """
    lines = text.splitlines()
    result = []
    in_code_block = False
    in_list = False
    in_blockquote = False
    output = []

    def emit_paragraph():
        nonlocal output
        if output:
            para = ' '.join(output)
            if para.strip():
                result.append(f'<p>{para}</p>')
            output = []

    for line in lines:
        # Code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                result.append('</code></pre>')
                in_code_block = False
            else:
                emit_paragraph()
                lang = line.strip()[3:] or ''
                result.append(f'<pre><code class="lang-{lang}">')
                in_code_block = True
            continue

        if in_code_block:
            result.append(line)
            continue

        # Blockquotes
        if line.strip().startswith('>'):
            if not in_blockquote:
                emit_paragraph()
                result.append('<blockquote>')
                in_blockquote = True
            result.append(line.strip()[1:])
            continue
        else:
            if in_blockquote:
                result.append('</blockquote>')
                in_blockquote = False

        # Headers
        m = re.match(r'^(#{1,3}) (.+)$', line)
        if m:
            emit_paragraph()
            level = len(m.group(1))
            result.append(f'<h{level}>{m.group(2)}</h{level}>')
            continue

        # HR
        if re.match(r'^---+$', line.strip()):
            emit_paragraph()
            result.append('<hr>')
            continue

        # List items
        m = re.match(r'^[-*] (.+)$', line)
        if m:
            if not in_list:
                emit_paragraph()
                result.append('<ul>')
                in_list = True
            result.append(f'<li>{basic_inline(m.group(1))}</li>')
            continue
        else:
            if in_list:
                result.append('</ul>')
                in_list = False

        # Empty line = paragraph break
        if not line.strip():
            emit_paragraph()
            continue

        # Regular text
        output.append(basic_inline(line))

    emit_paragraph()
    if in_list:
        result.append('</ul>')
    if in_blockquote:
        result.append('</blockquote>')

    return '\n'.join(result)


def basic_inline(text):
    """Handle inline markdown: bold, italic, code, links, images."""
    # Code spans
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Images ![alt](url) -- must run BEFORE links, since ![...] also contains [...]
    def img_replace(m):
        alt = m.group(1)
        url = m.group(2)
        return f'<img src="{url}" alt="{alt}" style="max-width:100%;">'
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', img_replace, text)
    # Links [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


def format_date(date_str):
    """Format YYYY-MM-DD to readable date."""
    try:
        d = datetime.strptime(date_str, '%Y-%m-%d')
        return d.strftime('%d %b %Y')
    except:
        return date_str


def read_posts():
    """Read all markdown posts from _posts directory."""
    posts = []
    if not os.path.exists(POSTS_DIR):
        print(f"Warning: {POSTS_DIR} not found")
        return posts

    for filename in sorted(os.listdir(POSTS_DIR)):
        if not filename.endswith('.md') or filename.startswith('TEMPLATE'):
            continue
        filepath = os.path.join(POSTS_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        fm, body = parse_frontmatter(content)
        if not fm.get('title'):
            print(f"Warning: {filename} missing title in frontmatter, skipping")
            continue

        slug = fm.get('slug') or slugify(fm['title'])
        excerpt = fm.get('excerpt', '')
        tag = fm.get('tag', 'update')
        date = fm.get('date', datetime.now().strftime('%Y-%m-%d'))
        html_content = basic_markdown(body.strip())

        posts.append({
            'slug': slug,
            'title': fm['title'],
            'date': format_date(date),
            'date_raw': date,
            'tag': tag,
            'excerpt': excerpt,
            'content': html_content,
            'body': body.strip(),
        })

    # Sort by date, newest first
    posts.sort(key=lambda p: p['date_raw'], reverse=True)
    return posts


def generate_post_page(post):
    """Generate a single post HTML file."""
    # Strip em-dashes from title for HTML output
    title = post['title'].replace('\u2014', '--')
    html = BASE_TEMPLATE.format(
        title=title,
        date=post['date'],
        tag=post['tag'],
        content=post['content'],
    )
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{post['slug']}.html")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  Generated: {out_path}")


def generate_index(posts):
    """Generate the devlog index page."""
    post_links = []
    for post in posts:
        # Strip em-dashes from title for HTML output
        title = post['title'].replace('\u2014', '--')
        post_links.append(POST_LINK_TEMPLATE.format(
            slug=post['slug'],
            title=title,
            date=post['date'],
            tag=post['tag'],
            excerpt=post['excerpt'],
        ))

    # If no posts, show placeholder
    if not post_links:
        post_links = ['      <p class="empty-state">No posts yet. Check back soon.</p>']

    html = INDEX_TEMPLATE.format(posts='\n'.join(post_links))
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_INDEX, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  Generated: {OUTPUT_INDEX}")


def main():
    print("Generating Vaelund devlog...")
    posts = read_posts()
    print(f"  Found {len(posts)} post(s)")
    generate_index(posts)
    for post in posts:
        generate_post_page(post)
    print("Done.")


if __name__ == '__main__':
    main()
