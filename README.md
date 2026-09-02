# Data Leadership Blog

A professional data leadership blog and custom static publishing system built in Python.

This repository serves two purposes:
1. It is the content repository for a professional portfolio focused on data strategy, governance, and leadership.
2. It is a lightweight, bespoke static site generator built with Python and Markdown, intentionally avoiding large frameworks to maintain absolute simplicity and technical transparency.

## Project Architecture

- **`content/`**: Markdown source files containing YAML frontmatter.
- **`templates/`**: HTML structural templates using Jinja2.
- **`static/`**: CSS and image assets.
- **`build.py`**: A procedural Python script that ingests the content, applies templates, and outputs the final HTML.
- **`_site/`**: The generated static website (built automatically, do not edit directly).

## How to Run Locally

1. Clone the repository.
2. Create a virtual environment (optional but recommended).
3. Install dependencies:
   ```bash
   pip install -r requirements.txt