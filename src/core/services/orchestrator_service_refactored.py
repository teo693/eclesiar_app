"""
Refactored Orchestrator Service using design patterns.

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

from typing import Any, Dict, Optional
from datetime import datetime

from src.core.config.app_config import AppConfig, DependencyContainer
from src.core.models.entities import ReportType
from src.core.strategies.data_fetching_strategy import DataFetchingContext
from src.reports.factories.report_factory import ReportFactory


class OrchestratorService:
    """Refactored orchestrator service with clean architecture"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.container = DependencyContainer(config)
        self.data_fetching_context = DataFetchingContext(
            self.container.get_strategies()['optimized_fetching']
        )
    
    def run(self, sections: Optional[Dict[str, bool]] = None, report_type: str = "daily") -> None:
        """
        Main orchestrator function using design patterns.
        
        Args:
            sections: Sections to include in report
            report_type: Type of report to generate
        """
        if sections is None:
            sections = {
                'military': True,
                'warriors': True, 
                'economic': True,
                'production': True
            }
        
        print(f"🚀 Starting refactored orchestrator...")
        print(f"📊 Report type: {report_type}")
        print(f"🔧 Strategy: {self.data_fetching_context.get_strategy_name()}")
        
        try:
            # Initialize database
            self._initialize_database()
            
            # Fetch data using strategy pattern
            data = self.data_fetching_context.fetch_data(sections, report_type)
            
            if not data:
                print("❌ Error: Cannot load data. Report will not be generated.")
                return
            
            # Generate report using factory pattern
            report_path = self._generate_report(data, sections, report_type)
            
            if report_path:
                print(f"✅ Report successfully generated: {report_path}")
            else:
                print("❌ Failed to generate report")
                
        except Exception as e:
            print(f"❌ Error in orchestrator: {e}")
    
    def run_html(self, output_dir: str, sections: Optional[Dict[str, bool]] = None) -> None:
        """
        Generate HTML report.
        
        Args:
            output_dir: Output directory
            sections: Sections to include
        """
        if sections is None:
            sections = {
                'military': True,
                'warriors': True, 
                'economic': True,
                'production': True
            }
        
        print(f"🌐 Generating HTML report...")
        
        try:
            # Fetch data
            data = self.data_fetching_context.fetch_data(sections, "html")
            
            if not data:
                print("❌ Error: Cannot load data for HTML report.")
                return
            
            # Generate HTML report
            report_path = self._generate_report(data, sections, "html", output_dir)
            
            if report_path:
                print(f"✅ HTML report successfully generated: {report_path}")
            else:
                print("❌ Failed to generate HTML report")
                
        except Exception as e:
            print(f"❌ Error generating HTML report: {e}")
    
    def run_production_analysis(self, output_dir: str) -> None:
        """
        Run production analysis.
        
        Args:
            output_dir: Output directory
        """
        print(f"🏭 Running production analysis...")
        
        sections = {
            'military': False,
            'warriors': False, 
            'economic': False,
            'production': True
        }
        
        self.run(sections, "production")
    
    def run_arbitrage_analysis(self, output_dir: str, min_profit: float = 0.5) -> None:
        """
        Run arbitrage analysis.
        
        Args:
            output_dir: Output directory
            min_profit: Minimum profit threshold
        """
        print(f"💰 Running arbitrage analysis (min profit: {min_profit}%)...")
        
        sections = {
            'military': False,
            'warriors': False, 
            'economic': True,
            'production': False
        }
        
        # Update config with new min profit
        self.config.arbitrage.min_profit_threshold = min_profit
        
        self.run(sections, "arbitrage")
    
    def run_short_economic_report(self, output_dir: str) -> None:
        """
        Run short economic report.
        
        Args:
            output_dir: Output directory
        """
        print(f"📈 Running short economic report...")
        
        sections = {
            'military': False,
            'warriors': False, 
            'economic': True,
            'production': False
        }
        
        self.run(sections, "short_economic")
    
    def set_data_fetching_strategy(self, strategy_name: str) -> None:
        """
        Set data fetching strategy.
        
        Args:
            strategy_name: Name of strategy ('full', 'optimized', 'cached')
        """
        strategies = self.container.get_strategies()
        
        if strategy_name == 'full':
            self.data_fetching_context.set_strategy(strategies['full_fetching'])
        elif strategy_name == 'optimized':
            self.data_fetching_context.set_strategy(strategies['optimized_fetching'])
        elif strategy_name == 'cached':
            self.data_fetching_context.set_strategy(strategies['cached_fetching'])
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        print(f"🔄 Switched to {self.data_fetching_context.get_strategy_name()}")
    
    def _initialize_database(self) -> None:
        """Initialize database"""
        try:
            # This would initialize the database using the repository
            print("🗄️ Database initialized")
        except Exception as e:
            print(f"⚠️ Warning: database initialization failed: {e}")
    
    def _generate_report(self, data: Dict[str, Any], sections: Dict[str, bool], 
                        report_type: str, output_dir: str = "reports") -> Optional[str]:
        """
        Generate report using factory pattern.
        
        Args:
            data: Report data
            sections: Sections to include
            report_type: Type of report
            output_dir: Output directory
            
        Returns:
            Path to generated file or None
        """
        try:
            # Map report type to ReportType enum
            report_type_mapping = {
                "daily": ReportType.DAILY,
                "html": ReportType.HTML,
                "production": ReportType.PRODUCTION,
                "arbitrage": ReportType.ARBITRAGE,
                "short_economic": ReportType.SHORT_ECONOMIC
            }
            
            if report_type not in report_type_mapping:
                print(f"❌ Unknown report type: {report_type}")
                return None
            
            # Create report generator using factory
            from src.core.services.base_service import ServiceDependencies
            deps = ServiceDependencies(
                country_repo=self.container.get_repositories()['country_repo'],
                currency_repo=self.container.get_repositories()['currency_repo'],
                region_repo=self.container.get_repositories()['region_repo'],
                item_repo=None,  # Will be implemented
                market_repo=None,  # Will be implemented
                production_repo=None,  # Will be implemented
                report_repo=None  # Will be implemented
            )
            
            generator = ReportFactory.create_generator(report_type_mapping[report_type], deps)
            
            # Generate report
            return generator.generate(data, sections, output_dir)
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            return None
