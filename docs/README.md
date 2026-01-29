# API Documentation

This directory contains the complete API documentation for the Cold Chain System.

## 📚 Documentation Structure

```
docs/
├── mkdocs.yml              # MkDocs configuration
├── requirements.txt        # Python dependencies for MkDocs
├── build.sh               # Build script
└── docs/                  # Markdown documentation files
    ├── index.md           # Homepage
    ├── getting-started.md # Getting started guide
    ├── authentication.md  # Authentication guide
    ├── error-handling.md  # Error handling guide
    ├── api-reference/     # API endpoint references
    │   ├── index.md
    │   ├── auth.md
    │   ├── analytics.md
    │   ├── ml-models.md
    │   └── ...
    ├── guides/            # How-to guides
    │   ├── creating-orders.md
    │   ├── optimizing-dispatch.md
    │   └── ...
    ├── examples/          # Code examples
    │   ├── python-examples.md
    │   ├── javascript-examples.md
    │   └── curl-examples.md
    ├── deployment/        # Deployment guides
    │   ├── production.md
    │   ├── docker.md
    │   └── ...
    └── changelog.md       # Version history
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Serve Documentation Locally

```bash
mkdocs serve
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

### 3. Build Documentation

```bash
./build.sh
# or
mkdocs build
```

Output will be in the `site/` directory.

### 4. Deploy to GitHub Pages

```bash
mkdocs gh-deploy
```

## 📝 Writing Documentation

### Markdown Format

Documentation is written in Markdown with Material for MkDocs extensions.

#### Code Blocks

```python
def hello_world():
    print("Hello, World!")
```

#### Admonitions

```markdown
!!! note "Note Title"
    This is a note.

!!! warning "Warning"
    This is a warning.

!!! info "Information"
    This is information.

!!! tip "Pro Tip"
    This is a tip.
```

#### Tabs

```markdown
=== "Python"
    ```python
    import requests
    response = requests.get("https://api.example.com")
    ```

=== "JavaScript"
    ```javascript
    fetch('https://api.example.com')
      .then(response => response.json())
      .then(data => console.log(data));
    ```
```

#### Tables

```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

## 🎨 Customization

### Theme Configuration

Edit `mkdocs.yml` to customize:
- Theme colors
- Navigation structure
- Plugins
- Extensions

### Adding New Pages

1. Create a new `.md` file in `docs/`
2. Add the page to `nav` section in `mkdocs.yml`
3. Rebuild documentation

## 🔗 Useful Links

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Markdown Guide](https://www.markdownguide.org/)
- [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/)

## 📊 Documentation Coverage

Current documentation includes:

- ✅ Getting Started Guide
- ✅ Authentication Guide
- ✅ API Reference (Analytics, ML Models, Security, etc.)
- ✅ Python Code Examples
- ✅ Deployment Guides
- ✅ Changelog

## 🛠️ Maintenance

### Updating Documentation

1. Edit relevant `.md` files
2. Test locally with `mkdocs serve`
3. Commit changes
4. Rebuild with `./build.sh` or `mkdocs build`
5. Deploy if needed with `mkdocs gh-deploy`

### Version Management

Update version numbers in:
- `mkdocs.yml` (site_url, version)
- `docs/changelog.md` (add new version entry)
- `docs/index.md` (current version badge)

## 📞 Support

For documentation issues or suggestions:
- **GitHub Issues**: [Create an issue](https://github.com/your-org/cold-chain/issues)
- **Email**: docs@coldchain.com

---

**Last Updated**: 2026-01-28  
**MkDocs Version**: 1.5.3  
**Material Theme**: 9.5.3
