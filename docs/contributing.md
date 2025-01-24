# Contributing

We welcome contributions to Earth Data Fetcher! Here's how you can help.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/lukegre/earth-data-fetcher.git
cd earth-data-fetcher
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/
```

## Documentation

The documentation is built using MkDocs. To preview the documentation locally:

```bash
mkdocs serve
```

Then visit `http://127.0.0.1:8000` in your browser.

## Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation if needed
6. Submit a pull request

## Code Style

We follow PEP 8 guidelines. Please ensure your code is formatted accordingly:

```bash
black src/
isort src/
```
