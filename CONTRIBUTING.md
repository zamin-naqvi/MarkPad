# Contributing to MarkPad

Thank you for your interest in contributing to MarkPad! We welcome contributions of all kinds.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Git

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/zamin-naqvi/MarkPad.git
cd markpad

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Run the app
python main.py
```

## 📋 How to Contribute

### Reporting Bugs
- Use the [GitHub Issues](https://github.com/zamin-naqvi/MarkPad/issues) tracker
- Include your OS, Python version, and steps to reproduce
- Attach screenshots if relevant

### Suggesting Features
- Open a [Feature Request](https://github.com/zamin-naqvi/MarkPad/issues/new?template=feature_request.md)
- Describe the use case and expected behavior

### Pull Requests

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/my-feature`
3. **Make your changes** and add tests if applicable
4. **Run tests**: `pytest`
5. **Format code**: `black markpad/`
6. **Commit**: `git commit -m "feat: add my feature"`
7. **Push**: `git push origin feature/my-feature`
8. **Open a Pull Request** against `main`

### Commit Messages
We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation
- `style:` — Code formatting
- `refactor:` — Code restructuring
- `test:` — Adding tests
- `chore:` — Maintenance

## 🏗️ Project Structure

```
markpad/
├── core/       # Rendering engine, settings, document model
├── ui/         # UI widgets (editor, preview, toolbar, graph)
├── dialogs/    # Modal dialogs
├── themes/     # Theme definitions and stylesheets
└── utils/      # Icon loading, helpers
```

## 📐 Code Style
- Use **Black** for formatting (line length: 100)
- Type hints are encouraged
- Docstrings for public methods

## 📄 License
By contributing, you agree that your contributions will be licensed under the MIT License.
