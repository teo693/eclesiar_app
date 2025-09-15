# Changelog

All notable changes to the Eclesiar Application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.5.0] - 2025-09-12

### Added
- **Docker Containerization** - Complete Docker setup with automated scheduling
- **Automated Reports** - Google Sheets reports generated every 6 hours via cron
- **Docker Compose** - Easy deployment with docker-compose.yml configuration
- **Volume Mounts** - Persistent data, logs, and reports storage
- **Health Checks** - Container health monitoring and automatic restart
- **Google Sheets CLI** - Added `google-sheets-report` command to main.py
- **Production Ready** - Resource limits, logging, and error handling
- **Easy Setup** - Automated startup scripts and comprehensive documentation
- **Environment Templates** - Docker configuration templates and examples
- **Docker Documentation** - Complete setup guide in DOCKER_SETUP.md

### Changed
- **Documentation Translation** - Translated all Polish documentation to English
- **File Organization** - Updated .dockerignore for optimized builds
- **Main Application** - Added Google Sheets report command support

### Technical Details
- Dockerfile with Python 3.11 base image
- Cron job scheduling every 6 hours
- Volume mounts for data persistence
- Health check monitoring
- Resource limits (512MB memory, 0.5 CPU)
- Comprehensive logging system

## [2.4.0] - 2025-09-10

### Added
- **Country Bonus System** - Implemented dynamic country bonus calculation based on regional bonuses
- **Enhanced Tables** - Added separate columns for regional and country bonuses in all reports
- **Formula Implementation** - Country bonus = sum of regional bonuses of same type in country / 5
- **Deduplication Logic** - Fixed duplicate region counting in country bonus calculations
- **Complete English Translation** - Translated all user-facing text, error messages, and code comments
- **Internationalization** - Application now fully supports English-speaking users
- **Code Documentation** - All docstrings and comments translated to English
- **User Interface** - All console menus, prompts, and output messages in English

### Changed
- **Report Format** - Enhanced productivity tables with country bonus columns
- **User Experience** - All interfaces now in English
- **Documentation** - Complete translation of all documentation files

## [2.3.0] - 2025-09-08

### Added
- **Interactive Production Calculator** - Full-featured calculator with region selection and parameter configuration
- **Quick Production Calculator** - Fast testing of different scenarios with predefined parameters
- **All 8 Production Factors** - Complete implementation from Eclesiar documentation
- **Region Selection** - Real-time data from API for region selection
- **Calculator Integration** - Integrated calculators with main application menu
- **New Commands** - Added `production-calculator` and `quick-calculator` commands
- **Comprehensive Documentation** - Created CALCULATOR_README.md with detailed usage instructions

### Changed
- **Application Interface** - Translated all interfaces to English
- **Menu System** - Enhanced interactive menu with new calculator options

## [2.2.0] - 2025-09-08

### Added
- **Short Economic Report** - New DOCX report generation
- **Currency Rates Analysis** - All currency rates vs GOLD
- **Cheapest Items** - Shows cheapest item of each type from all countries
- **Best Production Regions** - Displays best production region for each product
- **CLI Integration** - Added `short-economic-report` command
- **Menu Integration** - Added option to main application menu

### Changed
- **Report Generation** - Enhanced economic analysis capabilities
- **Output Formats** - Added DOCX format for economic reports

## [2.1.0] - 2025-09-08

### Added
- **NPC Wages Column** - Added to productivity table
- **English Translation** - Complete translation of entire application
- **Internationalization** - Full support for English-speaking users

### Fixed
- **Military Sections** - Fixed military sections appearing in economic reports
- **Report Accuracy** - Improved report content accuracy

### Changed
- **User Interface** - All console menus, prompts, and output messages in English
- **Documentation** - Updated README to English
- **Error Messages** - All error messages and warnings in English

## [2.0.0] - 2025-09-03

### Added
- **Main Entry Point** - Created `main.py` as central application interface
- **Command Line Interface** - Added support for command-line arguments
- **Interactive Menu** - User-friendly menu system
- **Report Organization** - Organized reports into separate folders
- **Project Structure** - Clean, organized project structure

### Changed
- **File Organization** - Removed duplicate files and consolidated code
- **Report Storage** - Reports now saved in dedicated folders
- **Code Consolidation** - Consolidated production and arbitrage analyzers
- **Documentation** - Updated and organized documentation

### Removed
- **Duplicate Files** - Removed all duplicate and backup files
- **Unused Code** - Cleaned up unused and test files
- **Redundant Analyzers** - Consolidated multiple analyzer versions

## [1.0.0] - 2025-09-01

### Added
- **Basic Reporting Functionality** - Initial report generation capabilities
- **Regional Productivity Analysis** - Basic productivity calculations
- **Currency Arbitrage Analysis** - Initial arbitrage detection
- **API Integration** - Basic Eclesiar API integration
- **Data Processing** - Core data processing and analysis

---

## Version History Summary

- **v2.5.0** - Docker automation and Google Sheets integration
- **v2.4.0** - Country bonus system and English translation
- **v2.3.0** - Production calculators with full functionality
- **v2.2.0** - Short economic reports in DOCX format
- **v2.1.0** - Complete English translation and internationalization
- **v2.0.0** - Major reorganization and cleanup
- **v1.0.0** - Initial release with basic functionality

## Future Roadmap

### Planned Features
- **Web Dashboard** - Browser-based interface for report viewing
- **Real-time Monitoring** - Live data updates and alerts
- **Advanced Analytics** - Machine learning for trend analysis
- **API Endpoints** - REST API for external integrations
- **Mobile Support** - Mobile-friendly interface
- **Cloud Deployment** - Kubernetes and cloud-native deployment options

### Technical Improvements
- **Performance Optimization** - Faster data processing and report generation
- **Caching System** - Intelligent caching for improved performance
- **Database Migration** - Support for PostgreSQL and other databases
- **Testing Suite** - Comprehensive unit and integration tests
- **CI/CD Pipeline** - Automated testing and deployment

---

**Copyright (c) 2025 Teo693**  
**Licensed under the MIT License**
