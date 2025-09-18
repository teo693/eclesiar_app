"""
Application configuration with dependency injection.

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration"""
    path: str
    connection_timeout: int = 30
    journal_mode: str = "WAL"
    foreign_keys: bool = True


@dataclass
class APIConfig:
    """API configuration"""
    base_url: str
    auth_token: str
    api_key: str
    timeout: int = 10
    max_retries: int = 3
    workers_market: int = 6
    workers_regions: int = 8
    workers_war: int = 4
    workers_hits: int = 4


@dataclass
class CacheConfig:
    """Cache configuration"""
    ttl_minutes: int = 5
    enabled: bool = True
    max_size: int = 1000


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    file_path: str = "logs/eclesiar.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class ArbitrageConfig:
    """Arbitrage configuration"""
    min_profit_threshold: float = 0.5
    min_spread_threshold: float = 0.001
    ticket_cost_gold: float = 0.1
    max_execution_time: int = 300


@dataclass
class AppConfig:
    """Main application configuration"""
    database: DatabaseConfig
    api: APIConfig
    cache: CacheConfig
    logging: LoggingConfig
    arbitrage: ArbitrageConfig
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables"""
        
        # Database configuration
        database = DatabaseConfig(
            path=os.getenv("DATABASE_PATH", "data/eclesiar.db"),
            connection_timeout=int(os.getenv("DB_CONNECTION_TIMEOUT", "30")),
            journal_mode=os.getenv("DB_JOURNAL_MODE", "WAL"),
            foreign_keys=os.getenv("DB_FOREIGN_KEYS", "true").lower() == "true"
        )
        
        # API configuration
        api = APIConfig(
            base_url=os.getenv("API_URL", "https://api.eclesiar.com"),
            auth_token=os.getenv("AUTH_TOKEN", ""),
            api_key=os.getenv("ECLESIAR_API_KEY", ""),
            timeout=int(os.getenv("API_TIMEOUT", "10")),
            max_retries=int(os.getenv("API_MAX_RETRIES", "3")),
            workers_market=int(os.getenv("API_WORKERS_MARKET", "6")),
            workers_regions=int(os.getenv("API_WORKERS_REGIONS", "8")),
            workers_war=int(os.getenv("API_WORKERS_WAR", "4")),
            workers_hits=int(os.getenv("API_WORKERS_HITS", "4"))
        )
        
        # Cache configuration
        cache = CacheConfig(
            ttl_minutes=int(os.getenv("CACHE_TTL_MINUTES", "5")),
            enabled=os.getenv("USE_CACHE", "true").lower() == "true",
            max_size=int(os.getenv("CACHE_MAX_SIZE", "1000"))
        )
        
        # Logging configuration
        logging = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            file_path=os.getenv("LOG_FILE", "logs/eclesiar.log"),
            max_file_size=int(os.getenv("LOG_MAX_FILE_SIZE", str(10 * 1024 * 1024))),
            backup_count=int(os.getenv("LOG_BACKUP_COUNT", "5"))
        )
        
        # Arbitrage configuration
        arbitrage = ArbitrageConfig(
            min_profit_threshold=float(os.getenv("MIN_PROFIT_THRESHOLD", "0.5")),
            min_spread_threshold=float(os.getenv("MIN_SPREAD_THRESHOLD", "0.001")),
            ticket_cost_gold=float(os.getenv("TICKET_COST_GOLD", "0.1")),
            max_execution_time=int(os.getenv("ARBITRAGE_MAX_EXECUTION_TIME", "300"))
        )
        
        return cls(
            database=database,
            api=api,
            cache=cache,
            logging=logging,
            arbitrage=arbitrage
        )
    
    def validate(self) -> bool:
        """Validate configuration"""
        errors = []
        
        # Validate required fields
        if not self.api.auth_token:
            errors.append("AUTH_TOKEN is required")
        
        if not self.api.base_url:
            errors.append("API_URL is required")
        
        # Validate paths
        db_dir = Path(self.database.path).parent
        if not db_dir.exists():
            try:
                db_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create database directory: {e}")
        
        log_dir = Path(self.logging.file_path).parent
        if not log_dir.exists():
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create log directory: {e}")
        
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True


class DependencyContainer:
    """Dependency injection container"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self._repositories = {}
        self._services = {}
        self._strategies = {}
    
    def get_repositories(self):
        """Get repository instances"""
        if not self._repositories:
            self._initialize_repositories()
        return self._repositories
    
    def get_services(self):
        """Get service instances"""
        if not self._services:
            self._initialize_services()
        return self._services
    
    def get_strategies(self):
        """Get strategy instances"""
        if not self._strategies:
            self._initialize_strategies()
        return self._strategies
    
    def _initialize_repositories(self):
        """Initialize repository instances"""
        from src.data.repositories.sqlite_repository import (
            SQLiteCountryRepository, SQLiteCurrencyRepository, SQLiteRegionRepository
        )
        
        self._repositories = {
            'country_repo': SQLiteCountryRepository(self.config.database.path),
            'currency_repo': SQLiteCurrencyRepository(self.config.database.path),
            'region_repo': SQLiteRegionRepository(self.config.database.path),
            # Add other repositories as they are implemented
        }
    
    def _initialize_services(self):
        """Initialize service instances"""
        from src.core.services.base_service import ServiceDependencies
        
        # Create service dependencies
        deps = ServiceDependencies(
            country_repo=self._repositories['country_repo'],
            currency_repo=self._repositories['currency_repo'],
            region_repo=self._repositories['region_repo'],
            item_repo=None,  # Will be implemented
            market_repo=None,  # Will be implemented
            production_repo=None,  # Will be implemented
            report_repo=None  # Will be implemented
        )
        
        self._services = {
            'economy_service': EconomyService(deps),
            # Add other services as they are implemented
        }
    
    def _initialize_strategies(self):
        """Initialize strategy instances"""
        from src.core.services.base_service import ServiceDependencies
        from src.core.strategies.data_fetching_strategy import (
            FullDataFetchingStrategy, OptimizedDataFetchingStrategy, CachedDataFetchingStrategy
        )
        
        # Ensure repositories are initialized first
        if not self._repositories:
            self._initialize_repositories()
        
        # Create service dependencies for strategies
        deps = ServiceDependencies(
            country_repo=self._repositories['country_repo'],
            currency_repo=self._repositories['currency_repo'],
            region_repo=self._repositories['region_repo'],
            item_repo=None,  # Will be implemented
            market_repo=None,  # Will be implemented
            production_repo=None,  # Will be implemented
            report_repo=None  # Will be implemented
        )
        
        self._strategies = {
            'full_fetching': FullDataFetchingStrategy(deps),
            'optimized_fetching': OptimizedDataFetchingStrategy(deps),
            'cached_fetching': CachedDataFetchingStrategy(deps, self.config.cache.ttl_minutes)
        }
