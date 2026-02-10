# RapidAI Documentation Site

Synthwave/Cyberpunk themed documentation site for RapidAI built with MkDocs Material. Made by Shaun

## Features

- 🌈 **Synthwave Cyberpunk Theme** - Neon colors, glowing effects, retro-futuristic design
- 📱 **Responsive** - Works on desktop, tablet, and mobile
- 🔍 **Search** - Full-text search across all documentation
- 📊 **Code Highlighting** - Beautiful syntax highlighting with custom theme
- 🎨 **Interactive** - Tabs, admonitions, and more
- ⚡ **Fast** - Static site, loads instantly

## Setup

### Install Dependencies

```bash
cd docsite
pip install -r requirements.txt
```

### Run Development Server

```bash
mkdocs serve
```

The site will be available at `http://localhost:8000`

### Build Static Site

```bash
mkdocs build
```

Output will be in the `site/` directory.

## Structure

```
docsite/
├── docs/                  # Documentation content
│   ├── index.md          # Homepage
│   ├── getting-started/  # Installation and first steps
│   ├── tutorial/         # Step-by-step tutorials
│   ├── advanced/         # Advanced features
│   ├── reference/        # API reference
│   ├── deployment/       # Deployment guides
│   ├── about/           # About, contributing, etc.
│   └── assets/          # CSS, JS, images
├── overrides/           # Theme customization
├── mkdocs.yml          # Configuration
└── requirements.txt    # Python dependencies
```

## Customization

### Colors

Edit `docs/assets/css/synthwave.css`:

```css
:root {
  --synthwave-pink: #ff006e;
  --synthwave-purple: #8338ec;
  --synthwave-blue: #3a86ff;
  --synthwave-cyan: #06ffa5;
  --synthwave-yellow: #ffbe0b;
}
```

### Theme

Edit `mkdocs.yml`:

```yaml
theme:
  name: material
  palette:
    primary: deep purple
    accent: pink
```

## Deployment

### GitHub Pages

```bash
mkdocs gh-deploy
```

### Netlify

1. Connect your GitHub repository
2. Build command: `mkdocs build`
3. Publish directory: `site`

### Vercel

1. Import your repository
2. Framework: Other
3. Build command: `mkdocs build`
4. Output directory: `site`

## Contributing

To add new documentation:

1. Create a new `.md` file in the appropriate directory
2. Add it to the `nav` section in `mkdocs.yml`
3. Test locally with `mkdocs serve`
4. Submit a pull request

## License

Same as RapidAI - MIT License
