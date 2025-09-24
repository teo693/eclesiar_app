# Requirements Files

## 📁 File Structure

- **`base.txt`** - Full requirements for local development and all features
- **`docker.txt`** - Optimized requirements for Docker environment only

## 🐳 Docker Requirements (`docker.txt`)

**Optimized for Docker environment** - contains only modules actually used:

### Core Dependencies
- `requests>=2.28.0` - HTTP requests for API calls
- `python-dotenv>=0.19.0` - Environment variable loading
- `urllib3>=1.26.0` - HTTP retry functionality

### Google Sheets Integration
- `google-api-python-client>=2.0.0` - Google Sheets API
- `google-auth>=2.0.0` - Google authentication
- `google-auth-oauthlib>=1.0.0` - OAuth2 authentication
- `google-auth-httplib2>=0.1.0` - HTTP transport for auth

### Data Analysis (Used in Reports)
- `pandas>=1.5.0` - Data manipulation
- `numpy>=1.21.0` - Numerical operations

### Visualization (Used in Daily/HTML Reports)
- `matplotlib>=3.5.0` - Plotting and charts
- `seaborn>=0.11.0` - Statistical visualization

### Document Export
- `python-docx>=0.8.11` - DOCX file generation

## 💻 Local Development Requirements (`base.txt`)

**Full feature set** for local development and testing:

### Includes everything from `docker.txt` plus:

### Additional Data Analysis
- `scipy>=1.9.0` - Scientific computing

### Additional Export Formats
- `openpyxl>=3.0.10` - Excel file support

### Additional HTTP Libraries
- `aiohttp>=3.8.0` - Async HTTP client
- `httpx>=0.23.0` - Modern HTTP client

### Configuration
- `pyyaml>=6.0` - YAML file support
- `configparser>=5.2.0` - Configuration file parsing

### Development Tools
- `pytest>=7.0.0` - Testing framework
- `pytest-asyncio>=0.20.0` - Async testing
- `black>=22.0.0` - Code formatting
- `flake8>=5.0.0` - Code linting
- `mypy>=0.991` - Type checking

## 🎯 Usage

### For Docker Deployment
```bash
# Docker automatically uses docker.txt
docker-compose up -d
```

### For Local Development
```bash
# Install full requirements
pip install -r requirements/base.txt
```

## 📊 Size Comparison

- **`docker.txt`**: ~12 packages (optimized for production)
- **`base.txt`**: ~20 packages (full development environment)

## 🔧 Benefits

1. **Faster Docker Builds**: Smaller requirements = faster image building
2. **Smaller Image Size**: Fewer dependencies = smaller Docker image
3. **Better Security**: Fewer packages = smaller attack surface
4. **Faster Container Startup**: Less to load = faster startup times
5. **Production Focus**: Only what's needed for Docker operation

## ⚠️ Notes

- Docker environment only generates **Google Sheets reports**
- Local development supports **all report types** (daily, HTML, production, arbitrage)
- Both environments use the same core application code
- Missing dependencies in Docker will cause import errors if trying to use unsupported features
