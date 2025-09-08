# Contributing to Eclesiar Application

Thank you for your interest in contributing to the Eclesiar Application! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Architecture Guidelines](#architecture-guidelines)
- [Contributing Process](#contributing-process)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)

## 🤝 Code of Conduct

This project follows a code of conduct that ensures a welcoming environment for all contributors. Please be respectful and constructive in all interactions.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a new branch** for your feature or bugfix
4. **Make your changes** following the guidelines below
5. **Test your changes** thoroughly
6. **Submit a pull request**

## 🛠️ Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Setup Steps

```bash
# Clone the repository
git clone https://github.com/Teo693/eclesiar-app.git
cd eclesiar-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/base.txt

# Install development dependencies
pip install black flake8 mypy pytest

# Copy environment configuration
cp .env.example .env
# Edit .env with your API credentials
```

## 🏗️ Architecture Guidelines

This project follows **Clean Architecture** principles with design patterns:

### Repository Pattern
- Add new entities to `src/core/models/entities.py`
- Create repository interfaces in `src/core/models/repositories.py`
- Implement repositories in `src/data/repositories/`

### Service Layer Pattern
- Business logic goes in `src/core/services/`
- Use dependency injection via `ServiceDependencies`
- Extend `BaseService` for new services

### Factory Pattern
- Register new report generators in `src/reports/factories/report_factory.py`
- Implement `ReportGenerator` interface

### Strategy Pattern
- Add new strategies in `src/core/strategies/`
- Implement `DataFetchingStrategy` interface

## 📝 Contributing Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-description
```

### 2. Make Changes

- Follow the architecture guidelines
- Write clean, readable code
- Add appropriate comments and docstrings
- Update documentation if needed

### 3. Test Your Changes

```bash
# Run linting
flake8 src/ tests/

# Run type checking
mypy src/

# Format code
black src/ tests/

# Run tests (when implemented)
pytest tests/
```

### 4. Commit Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add new report generator for market analysis"
git commit -m "fix: resolve memory leak in data fetching strategy"
git commit -m "docs: update API documentation"
```

### 5. Submit Pull Request

- Provide a clear description of your changes
- Reference any related issues
- Include screenshots for UI changes
- Ensure all tests pass

## 🎨 Code Style

### Python Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write descriptive docstrings
- Keep functions small and focused

### Naming Conventions

- **Classes**: PascalCase (`ProductionAnalyzer`)
- **Functions/Variables**: snake_case (`fetch_data`)
- **Constants**: UPPER_SNAKE_CASE (`API_BASE_URL`)
- **Files**: snake_case (`data_fetching_strategy.py`)

### Example Code Structure

```python
"""
Module description.

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

from typing import List, Optional
from dataclasses import dataclass

from src.core.models.entities import Country


@dataclass
class AnalysisResult:
    """Result of data analysis."""
    countries: List[Country]
    score: float


class DataAnalyzer:
    """Analyzes game data for insights."""
    
    def __init__(self, repository: CountryRepository):
        """Initialize analyzer with repository."""
        self.repository = repository
    
    def analyze_countries(self) -> AnalysisResult:
        """
        Analyze countries data.
        
        Returns:
            AnalysisResult with countries and score
        """
        countries = self.repository.find_all()
        score = self._calculate_score(countries)
        return AnalysisResult(countries=countries, score=score)
    
    def _calculate_score(self, countries: List[Country]) -> float:
        """Calculate analysis score."""
        return len(countries) * 0.1
```

## 🧪 Testing

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_entities.py
│   ├── test_services.py
│   └── test_repositories.py
├── integration/             # Integration tests
│   ├── test_api_client.py
│   └── test_database.py
└── fixtures/                # Test data
    ├── sample_data.json
    └── mock_responses.py
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock

from src.core.models.entities import Country
from src.core.services.economy_service import EconomyService


class TestEconomyService:
    """Test cases for EconomyService."""
    
    def test_get_countries_success(self):
        """Test successful country retrieval."""
        # Arrange
        mock_repo = Mock()
        mock_repo.find_all.return_value = [
            Country(id=1, name="Test Country", currency_id=1, currency_name="GOLD")
        ]
        service = EconomyService(mock_repo)
        
        # Act
        result = service.get_countries_and_currencies()
        
        # Assert
        assert len(result[0]) == 1
        assert result[0][1]['name'] == "Test Country"
```

## 📚 Documentation

### Code Documentation

- Use docstrings for all public methods
- Include type hints
- Document complex algorithms
- Add examples where helpful

### README Updates

- Update feature lists
- Add new configuration options
- Update installation instructions
- Include new examples

### API Documentation

- Document new endpoints
- Include request/response examples
- Update troubleshooting guides

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Description** of the issue
2. **Steps to reproduce**
3. **Expected behavior**
4. **Actual behavior**
5. **Environment details** (OS, Python version, etc.)
6. **Error messages** or logs

## ✨ Feature Requests

For feature requests, please provide:

1. **Clear description** of the feature
2. **Use case** and motivation
3. **Proposed implementation** (if you have ideas)
4. **Alternative solutions** considered

## 📞 Getting Help

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Email**: Contact Teo693 for direct communication

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the Eclesiar Application! 🎮
