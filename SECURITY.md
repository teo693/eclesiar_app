# Security Guidelines

## 🔐 Important Security Information

This application handles sensitive data including API keys, database files, and Google Sheets credentials. **NEVER commit sensitive files to GitHub.**

## 🚫 Files That Should NEVER Be Committed

The following files are automatically ignored by Git and should never be committed:

### Environment Variables
- `.env` - Contains API keys and sensitive configuration
- `.env.local`, `.env.production`, `.env.staging` - Environment-specific configs
- `*.env` - Any environment files

### Credentials and Keys
- `cred/google_credentials.json` - Google service account credentials
- `cred/oauth2_credentials.json` - OAuth2 credentials
- `*.key`, `*.token` - Any key or token files
- `auth_token.txt`, `api_key.txt` - API authentication files

### Database Files
- `data/*.db` - SQLite database files
- `data/*.json` - Cached API data
- `raw_api_output.json` - Raw API responses
- `historia_raportow.json` - Historical report data

### Generated Files
- `reports/` - All generated reports
- `logs/` - Application logs
- `__pycache__/` - Python cache files

## ✅ Safe to Commit

The following files are safe to commit to GitHub:

- Source code (`.py` files)
- Documentation (`.md` files)
- Configuration templates (`env.example`)
- `.gitignore` file
- `requirements/` files
- `config/settings/` files (without sensitive data)

## 🛡️ Security Best Practices

### 1. Environment Variables
Always use environment variables for sensitive configuration:

```python
# ✅ Good - uses environment variable
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "")

# ❌ Bad - hardcoded value
AUTH_TOKEN = "eclesiar_prod_abc123"
```

### 2. Configuration Files
Use example files for configuration templates:

```bash
# Copy example configuration
cp env.example .env

# Edit with your actual values
nano .env
```

### 3. Credentials Management
- Store credentials in environment variables
- Use service accounts for Google APIs
- Rotate keys regularly
- Never log sensitive data

### 4. Database Security
- Use environment variables for database paths
- Don't commit database files
- Use proper file permissions

## 🔍 Pre-Commit Checklist

Before committing to GitHub, verify:

- [ ] No `.env` files in the commit
- [ ] No credential files (`cred/*.json`)
- [ ] No database files (`*.db`)
- [ ] No API keys in source code
- [ ] No sensitive URLs or IDs hardcoded
- [ ] All sensitive data uses environment variables

## 🚨 If You Accidentally Commit Sensitive Data

If you accidentally commit sensitive data:

1. **Immediately remove the sensitive data** from the repository
2. **Rotate any exposed credentials** (API keys, passwords)
3. **Use git history rewriting** to remove the sensitive data from history:
   ```bash
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch path/to/sensitive/file' \
   --prune-empty --tag-name-filter cat -- --all
   ```
4. **Force push** to update the remote repository:
   ```bash
   git push origin --force --all
   ```

## 📋 Environment Variables Reference

### Required Variables
```bash
# API Configuration
AUTH_TOKEN="eclesiar_prod_your_api_key"
ECLESIAR_API_KEY=""

# Google Sheets (if using)
GOOGLE_PROJECT_ID="your-project-id"
GOOGLE_SERVICE_ACCOUNT_EMAIL="service@project.iam.gserviceaccount.com"
GOOGLE_SHEETS_EXISTING_ID="spreadsheet-id"
```

### Optional Variables
```bash
# Database
DATABASE_PATH="data/eclesiar.db"

# API Settings
API_TIMEOUT="10"
API_MAX_RETRIES="3"

# Cache
CACHE_TTL_MINUTES="5"
USE_CACHE="true"
```

## 🔧 Validation Commands

Check your configuration for security issues:

```bash
# Check for hardcoded API keys
grep -r "eclesiar_prod_" src/ --exclude-dir=__pycache__

# Check for exposed credentials
grep -r "google_credentials" . --exclude-dir=.git

# Validate environment setup
python3 -c "import os; print('✅ .env loaded' if os.getenv('AUTH_TOKEN') else '❌ No AUTH_TOKEN')"
```

## 📞 Support

If you have security concerns or questions:

1. Review this document
2. Check the troubleshooting guides
3. Verify your `.gitignore` configuration
4. Test with the validation commands above

Remember: **When in doubt, don't commit it!**
