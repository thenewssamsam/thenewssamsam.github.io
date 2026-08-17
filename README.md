# Beyond The News Sam - GitHub Pages Website

A fully automated news commentary website powered by AI and GitHub Pages.

## Features

- ✅ Completely free hosting (GitHub Pages)
- ✅ Fully automated article generation and deployment
- ✅ Support for Google AdSense
- ✅ Responsive design
- ✅ SEO optimized

## Setup Instructions

### 1. Create GitHub Repository

Create a new repository named `thenewssamsam.github.io` on GitHub.

### 2. Push This Code

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/thenewssamsam/thenewssamsam.github.io.git
git push -u origin main
```

### 3. Add AdSense

Replace `ca-pub-XXXXXXXXX` in `_layouts/post.html` with your actual AdSense publisher ID.

### 4. Automate Article Generation

Use GitHub Actions to automatically generate and publish articles.

## Directory Structure

```
_config.yml          - Jekyll configuration
_layouts/            - Page templates
_posts/              - Blog articles (auto-generated)
assets/              - CSS and JavaScript
index.html           - Homepage
about.md             - About page
```

## Automation Script

The automation script should:
1. Generate articles as Markdown files
2. Place them in `_posts/` directory with format: `YYYY-MM-DD-title.md`
3. Commit and push to GitHub
4. GitHub Pages automatically builds and deploys

## Article Format

Articles should be Markdown files with front matter:

```markdown
---
layout: post
title: Article Title
date: 2026-08-17 14:30:00 +0800
categories: news
tags: [tag1, tag2]
author: Sam
---

Article content here...
```

## Local Testing

To test locally:

```bash
gem install jekyll bundler
bundle install
bundle exec jekyll serve
```

Visit `http://localhost:4000` in your browser.

---

*Automated by your Python script*
