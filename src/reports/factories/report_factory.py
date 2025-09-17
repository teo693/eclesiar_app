"""
Factory Pattern implementation for report generators.

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from enum import Enum

from src.core.models.entities import ReportType, ReportData
from src.core.services.base_service import ServiceDependencies


class ReportGenerator(ABC):
    """Abstract base class for report generators"""
    
    def __init__(self, dependencies: ServiceDependencies):
        self.deps = dependencies
    
    @abstractmethod
    def generate(self, data: Dict[str, Any], sections: Dict[str, bool], output_dir: str) -> Optional[str]:
        """
        Generate report.
        
        Args:
            data: Report data
            sections: Sections to include
            output_dir: Output directory
            
        Returns:
            Path to generated file or None if failed
        """
        pass
    
    @abstractmethod
    def get_report_type(self) -> ReportType:
        """Get report type"""
        pass


class DailyReportGenerator(ReportGenerator):
    """Daily report generator"""
    
    def generate(self, data: Dict[str, Any], sections: Dict[str, bool], output_dir: str) -> Optional[str]:
        """Generate daily DOCX report"""
        try:
            from ..generators.daily_report import generate_report
            
            return generate_report(
                summary_data=data.get('summary_data', {}),
                historical_data=data.get('historical_data', {}),
                top_warriors=data.get('top_warriors', {}),
                items_map=data.get('items_map', {}),
                currencies_map=data.get('currencies_map', {}),
                country_map=data.get('country_map', {}),
                currency_codes_map=data.get('currency_codes_map', {}),
                gold_id=data.get('gold_id'),
                output_dir=output_dir,
                sections=sections
            )
        except Exception as e:
            print(f"Error generating daily report: {e}")
            return None
    
    def get_report_type(self) -> ReportType:
        return ReportType.DAILY


class HTMLReportGenerator(ReportGenerator):
    """HTML report generator"""
    
    def generate(self, data: Dict[str, Any], sections: Dict[str, bool], output_dir: str) -> Optional[str]:
        """Generate HTML report"""
        try:
            from ..generators.html_report import generate_html_report
            
            return generate_html_report(
                summary_data=data.get('summary_data', {}),
                historical_data=data.get('historical_data', {}),
                top_warriors=data.get('top_warriors', {}),
                items_map=data.get('items_map', {}),
                currencies_map=data.get('currencies_map', {}),
                country_map=data.get('country_map', {}),
                currency_codes_map=data.get('currency_codes_map', {}),
                gold_id=data.get('gold_id'),
                output_dir=output_dir,
                sections=sections
            )
        except Exception as e:
            print(f"Error generating HTML report: {e}")
            return None
    
    def get_report_type(self) -> ReportType:
        return ReportType.HTML


class ProductionReportGenerator(ReportGenerator):
    """Production analysis report generator"""
    
    def generate(self, data: Dict[str, Any], sections: Dict[str, bool], output_dir: str) -> Optional[str]:
        """Generate production analysis report"""
        try:
            from ..generators.production_report import ProductionAnalyzer
            
            analyzer = ProductionAnalyzer()
            return analyzer.generate_report(output_dir)
        except Exception as e:
            print(f"Error generating production report: {e}")
            return None
    
    def get_report_type(self) -> ReportType:
        return ReportType.PRODUCTION


class ArbitrageReportGenerator(ReportGenerator):
    """Arbitrage analysis report generator"""
    
    def generate(self, data: Dict[str, Any], sections: Dict[str, bool], output_dir: str) -> Optional[str]:
        """Generate arbitrage analysis report"""
        try:
            from ..generators.arbitrage_report import CurrencyArbitrageAnalyzer
            
            analyzer = CurrencyArbitrageAnalyzer()
            return analyzer.generate_report(output_dir)
        except Exception as e:
            print(f"Error generating arbitrage report: {e}")
            return None
    
    def get_report_type(self) -> ReportType:
        return ReportType.ARBITRAGE


class ShortEconomicReportGenerator(ReportGenerator):
    """Short economic report generator"""
    
    def generate(self, data: Dict[str, Any], sections: Dict[str, bool], output_dir: str) -> Optional[str]:
        """Generate short economic report"""
        try:
            from ..generators.short_economic_report import generate_short_economic_report
            
            return generate_short_economic_report(output_dir, sections)
        except Exception as e:
            print(f"Error generating short economic report: {e}")
            return None
    
    def get_report_type(self) -> ReportType:
        return ReportType.SHORT_ECONOMIC


class GoogleSheetsReportGenerator(ReportGenerator):
    """Google Sheets report generator"""
    
    def generate(self, data: Dict[str, Any], sections: Dict[str, bool], output_dir: str) -> Optional[str]:
        """Generate Google Sheets report"""
        try:
            from ..exporters.google_sheets_exporter import GoogleSheetsExporter
            
            exporter = GoogleSheetsExporter(self.deps)
            return exporter.generate(data, sections, output_dir)
        except Exception as e:
            print(f"Error generating Google Sheets report: {e}")
            return None
    
    def get_report_type(self) -> ReportType:
        return ReportType.GOOGLE_SHEETS


class ReportFactory:
    """Factory for creating report generators"""
    
    _generators = {
        ReportType.DAILY: DailyReportGenerator,
        ReportType.HTML: HTMLReportGenerator,
        ReportType.PRODUCTION: ProductionReportGenerator,
        ReportType.ARBITRAGE: ArbitrageReportGenerator,
        ReportType.SHORT_ECONOMIC: ShortEconomicReportGenerator,
        ReportType.GOOGLE_SHEETS: GoogleSheetsReportGenerator,
    }
    
    @classmethod
    def create_generator(cls, report_type: ReportType, dependencies: ServiceDependencies) -> ReportGenerator:
        """
        Create report generator for specified type.
        
        Args:
            report_type: Type of report to generate
            dependencies: Service dependencies
            
        Returns:
            Report generator instance
            
        Raises:
            ValueError: If report type is not supported
        """
        if report_type not in cls._generators:
            raise ValueError(f"Unsupported report type: {report_type}")
        
        generator_class = cls._generators[report_type]
        return generator_class(dependencies)
    
    @classmethod
    def get_supported_types(cls) -> list[ReportType]:
        """Get list of supported report types"""
        return list(cls._generators.keys())
    
    @classmethod
    def register_generator(cls, report_type: ReportType, generator_class: type[ReportGenerator]):
        """
        Register new report generator.
        
        Args:
            report_type: Report type
            generator_class: Generator class
        """
        cls._generators[report_type] = generator_class
