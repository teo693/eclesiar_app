"""
Enhanced Google Sheets Data Formatter
Tworzy merytoryczne tabele z pełną analizą ekonomiczną

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import json
from src.core.services.calculations.market_calculation_service import MarketCalculationService
from src.core.services.calculations.currency_calculation_service import CurrencyCalculationService
from src.core.services.calculations.region_calculation_service import RegionCalculationService

class EnhancedSheetsFormatter:
    """Enhanced formatter for comprehensive economic analysis in Google Sheets"""
    
    def __init__(self):
        self.date_format = "%Y-%m-%d %H:%M:%S"
        
        # Initialize centralized calculation services (zgodnie z planem refaktoryzacji)
        self.market_calc = MarketCalculationService()
        self.currency_calc = CurrencyCalculationService()
        self.region_calc = RegionCalculationService()
    
    def format_comprehensive_economic_report(self, data: Dict[str, Any]) -> Dict[str, List[List]]:
        """
        Formatuje kompletny raport ekonomiczny z 6 merytorycznymi arkuszami
        """
        sheets_data = {}
        
        # Extract all data
        country_map = data.get('country_map', {})
        currencies_map = data.get('currencies_map', {})
        currency_codes_map = data.get('currency_codes_map', {})
        currency_rates = data.get('currency_rates', {})
        historical_data = data.get('historical_data', {})
        best_jobs = data.get('best_jobs', [])
        cheapest_items = data.get('cheapest_items', {})
        regions_data = data.get('regions_data', [])
        gold_id = data.get('gold_id')
        
        # 1. 💰 Currency Analysis - Kompleksowa analiza walut
        sheets_data["💰 Currency Analysis"] = self._create_currency_analysis_sheet(
            currency_rates, currencies_map, currency_codes_map, historical_data, gold_id
        )
        
        # 2. 🚀 Premium Job Opportunities - Najlepsze oferty pracy (NOWY ARKUSZ)
        sheets_data["🚀 Premium Job Opportunities"] = self._create_premium_jobs_sheet(
            best_jobs, country_map, currency_rates, gold_id
        )
        
        # 3. 🛒 Market Opportunities - Okazje zakupowe
        sheets_data["🛒 Market Opportunities"] = self._create_market_opportunities_sheet(
            cheapest_items, currencies_map
        )
        
        # 4. 🏭 Production Hubs - Lokalizacje produkcyjne
        sheets_data["🏭 Production Hubs"] = self._create_production_hubs_sheet(
            regions_data
        )
        
        # 5. 📊 Economic Overview - Przegląd gospodarczy
        sheets_data["📊 Economic Overview"] = self._create_economic_overview_sheet(
            country_map, currency_rates, currencies_map, regions_data, best_jobs
        )
        
        # 6. ⚡ Investment Alerts - Alerty inwestycyjne
        sheets_data["⚡ Investment Alerts"] = self._create_investment_alerts_sheet(
            currency_rates, cheapest_items, best_jobs, regions_data, historical_data
        )
        
        return sheets_data
    
    def _create_currency_analysis_sheet(self, currency_rates: Dict, currencies_map: Dict, 
                                      currency_codes_map: Dict, historical_data: Dict, 
                                      gold_id: int) -> List[List]:
        """Arkusz 1: Kompleksowa analiza walut"""
        
        sheet = [
            ["💰 CURRENCY ANALYSIS - COMPREHENSIVE MARKET DATA", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["Currency Name", "Code", "Rate vs GOLD", "Previous Rate", "Change %", 
             "Strength Rank", "Volatility", "Investment Grade"]
        ]
        
        if not currency_rates:
            sheet.append(["No currency data available", "", "", "", "", "", "", ""])
            return sheet
        
        # Pobierz wczorajsze kursy
        yesterday_key = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        yesterday_rates = {}
        
        try:
            if yesterday_key in historical_data:
                yesterday_rates = (historical_data[yesterday_key].get('economic_summary') or {}).get('currency_rates') or {}
        except:
            pass
        
        # Przygotuj dane do analizy
        currency_analysis = []
        
        for currency_id, rate in currency_rates.items():
            currency_data = currencies_map.get(str(currency_id), {})
            if isinstance(currency_data, dict):
                currency_name = currency_data.get('name', f'Currency {currency_id}')
            else:
                currency_name = str(currency_data)
            
            currency_code = currency_codes_map.get(currency_id, "")
            
            # Oblicz zmianę
            prev_rate = yesterday_rates.get(str(currency_id))
            change_pct = 0
            change_text = "—"
            
            if prev_rate and isinstance(prev_rate, (int, float)) and prev_rate > 0:
                change_pct = ((rate - prev_rate) / prev_rate) * 100
                arrow = "📈" if change_pct > 0 else ("📉" if change_pct < 0 else "➡️")
                change_text = f"{arrow} {change_pct:+.2f}%"
            
            # Oblicz siłę waluty (pozycja względem innych)
            volatility_score = abs(change_pct) if change_pct != 0 else 0
            
            # Ocena inwestycyjna
            if rate > 0.4:
                investment_grade = "🔥 STRONG"
            elif rate > 0.2:
                investment_grade = "✅ GOOD" 
            elif rate > 0.1:
                investment_grade = "⚠️ MEDIUM"
            else:
                investment_grade = "❌ WEAK"
            
            currency_analysis.append({
                'name': currency_name,
                'code': currency_code,
                'rate': rate,
                'prev_rate': prev_rate or 0,
                'change_pct': change_pct,
                'change_text': change_text,
                'volatility': volatility_score,
                'investment_grade': investment_grade
            })
        
        # Sortuj według siły (rate)
        currency_analysis.sort(key=lambda x: x['rate'], reverse=True)
        
        # Dodaj rankingi
        for i, currency in enumerate(currency_analysis, 1):
            sheet.append([
                currency['name'],
                currency['code'],
                f"{currency['rate']:.6f}",
                f"{currency['prev_rate']:.6f}" if currency['prev_rate'] > 0 else "—",
                currency['change_text'],
                f"#{i}",
                f"{currency['volatility']:.2f}%",
                currency['investment_grade']
            ])
        
        return sheet
    
    def _create_premium_jobs_sheet(self, best_jobs: List, country_map: Dict, 
                                 currency_rates: Dict, gold_id: int) -> List[List]:
        """Arkusz 2: Szczegółowa analiza najlepszych ofert pracy - GŁÓWNY ARKUSZ PRACY"""
        
        sheet = [
            ["🚀 PREMIUM JOB OPPORTUNITIES - DETAILED SALARY ANALYSIS", "", "", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", "", "", ""],
            ["Business", "Country", "Salary GOLD", "Salary Local", "Currency", "Eco Skill", 
             "Global Rank", "Country Rank", "Efficiency", "Weekly Estimate", "Monthly Estimate", "Action"]
        ]
        
        if not best_jobs:
            # Pobierz dane używając centralnego serwisu jeśli nie ma danych
            try:
                if country_map and currency_rates and gold_id:
                    job_offers = self.market_calc.fetch_best_jobs_from_all_countries(country_map, currency_rates, gold_id)
                    best_jobs = self.market_calc.convert_job_offers_to_legacy_format(job_offers)
                    best_jobs.sort(key=lambda x: x.get("salary_gold", 0), reverse=True)
            except Exception as e:
                print(f"⚠️ Error fetching job data for premium analysis: {e}")
                pass
        
        if not best_jobs:
            sheet.append(["No premium job data available", "", "", "", "", "", "", "", "", "", "", ""])
            return sheet
        
        # Sortuj i weź top 50 ofert dla szczegółowej analizy
        best_jobs_sorted = sorted(best_jobs, key=lambda x: x.get("salary_gold", 0), reverse=True)[:50]
        
        # Grupuj oferty według krajów dla rankingu krajowego
        country_jobs = {}
        for job in best_jobs_sorted:
            country = job.get('country_name', 'Unknown')
            if country not in country_jobs:
                country_jobs[country] = []
            country_jobs[country].append(job)
        
        # Sortuj oferty w każdym kraju
        for country in country_jobs:
            country_jobs[country].sort(key=lambda x: x.get("salary_gold", 0), reverse=True)
        
        # Oblicz średnie i statystyki
        avg_global_salary = sum(job.get('salary_gold', 0) for job in best_jobs) / len(best_jobs) if best_jobs else 0
        median_salary = sorted([job.get('salary_gold', 0) for job in best_jobs])[len(best_jobs)//2] if best_jobs else 0
        
        # Przygotuj dane dla każdej oferty
        for global_rank, job in enumerate(best_jobs_sorted, 1):
            country = job.get('country_name', 'Unknown')
            business_id = job.get('business_id') or job.get('company_id') or f"Job-{global_rank}"
            salary_gold = job.get('salary_gold', 0)
            salary_local = job.get('salary_original', 0)
            currency = job.get('currency_name', 'N/A')
            eco_skill = job.get('economic_skill', 0)
            
            # Znajdź ranking w kraju
            country_rank = 1
            for i, country_job in enumerate(country_jobs.get(country, []), 1):
                if country_job.get('business_id') == job.get('business_id'):
                    country_rank = i
                    break
            
            # Oblicz efektywność (płaca do wymagań skill)
            if eco_skill > 0:
                efficiency = salary_gold / eco_skill
                efficiency_text = f"{efficiency:.4f}"
            else:
                efficiency_text = "∞ (No req.)"
            
            # Szacunkowe zarobki (założenie: praca codziennie)
            weekly_estimate = salary_gold * 7
            monthly_estimate = salary_gold * 30
            
            # Rekomendacja działania
            if salary_gold > avg_global_salary * 1.5:
                action = "🔥 APPLY NOW!"
            elif salary_gold > avg_global_salary * 1.2:
                action = "✅ Highly Recommended"
            elif salary_gold > median_salary:
                action = "👍 Consider"
            else:
                action = "📊 Monitor"
            
            sheet.append([
                str(business_id),
                country,
                f"{salary_gold:.6f}",
                f"{salary_local:.2f}",
                currency,
                str(eco_skill) if eco_skill > 0 else "No req.",
                f"#{global_rank}",
                f"#{country_rank} in {country}",
                efficiency_text,
                f"{weekly_estimate:.4f}",
                f"{monthly_estimate:.3f}",
                action
            ])
        
        # Dodaj separator i statystyki na końcu
        sheet.append(["", "", "", "", "", "", "", "", "", "", "", ""])
        sheet.append(["📊 MARKET STATISTICS", "", "", "", "", "", "", "", "", "", "", ""])
        sheet.append(["Global Average Salary", f"{avg_global_salary:.6f}", "", "", "", "", "", "", "", "", "", ""])
        sheet.append(["Median Salary", f"{median_salary:.6f}", "", "", "", "", "", "", "", "", "", ""])
        sheet.append(["Total Analyzed Jobs", str(len(best_jobs_sorted)), "", "", "", "", "", "", "", "", "", ""])
        sheet.append(["Countries Covered", str(len(country_jobs)), "", "", "", "", "", "", "", "", "", ""])
        
        return sheet
    
    def _create_market_opportunities_sheet(self, cheapest_items: Dict, 
                                         currencies_map: Dict) -> List[List]:
        """Arkusz 3: Okazje zakupowe na rynku"""
        
        sheet = [
            ["🛒 MARKET OPPORTUNITIES - BEST DEALS BY PRODUCT", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", ""],
            ["Product", "Quality", "Best Price (GOLD)", "Country", "Price (Local)", 
             "Currency", "Stock", "5-Day Avg", "Discount %", "Deal Rating"]
        ]
        
        if not cheapest_items:
            sheet.append(["No market data available", "", "", "", "", "", "", "", "", ""])
            return sheet
        
        # Mapowanie nazw produktów
        item_names = {
            1: "Grain", 2: "Food Q1", 3: "Food Q2", 4: "Food Q3", 5: "Food Q4", 6: "Food Q5",
            7: "Iron", 8: "Weapon Q1", 9: "Weapon Q2", 10: "Weapon Q3", 11: "Weapon Q4", 12: "Weapon Q5",
            13: "Fuel", 14: "Tickets Q1", 15: "Tickets Q2", 16: "Tickets Q3", 17: "Tickets Q4", 18: "Tickets Q5",
            19: "Titanium", 20: "Aircraft Q1", 21: "Aircraft Q2", 22: "Aircraft Q3", 23: "Aircraft Q4", 24: "Aircraft Q5"
        }
        
        # Zbierz wszystkie oferty
        all_opportunities = []
        
        for item_id, items_list in cheapest_items.items():
            if not items_list:
                continue
            
            item_name = item_names.get(item_id, f"Item {item_id}")
            quality = "Q1" if "Q" not in item_name else item_name.split()[-1]
            product_base = item_name.replace(f" {quality}", "") if quality != "Q1" else item_name
            
            # Znajdź najlepszą ofertę
            best_item = min(items_list, key=lambda x: x.get('price_gold', float('inf')))
            
            price_gold = best_item.get('price_gold', 0)
            country = best_item.get('country', 'Unknown')
            price_local = best_item.get('price_currency', best_item.get('price_in_currency', 0))
            currency = best_item.get('currency_name', 'N/A')
            stock = best_item.get('amount', 0)
            avg5 = best_item.get('avg5_in_gold', 0)
            
            # Oblicz rabat względem średniej
            discount_pct = 0
            if avg5 > 0:
                discount_pct = ((avg5 - price_gold) / avg5) * 100
            
            # Ocena okazji
            if discount_pct > 20:
                deal_rating = "💎 AMAZING"
            elif discount_pct > 10:
                deal_rating = "🔥 GREAT"
            elif discount_pct > 5:
                deal_rating = "✅ GOOD"
            elif discount_pct > 0:
                deal_rating = "👍 FAIR"
            else:
                deal_rating = "📊 MARKET"
            
            all_opportunities.append({
                'product': product_base,
                'quality': quality,
                'price_gold': price_gold,
                'country': country,
                'price_local': price_local,
                'currency': currency,
                'stock': stock,
                'avg5': avg5,
                'discount_pct': discount_pct,
                'deal_rating': deal_rating
            })
        
        # Sortuj według rabatu (najlepsze okazje pierwsze)
        all_opportunities.sort(key=lambda x: x['discount_pct'], reverse=True)
        
        # Dodaj do arkusza (top 30 okazji)
        for opp in all_opportunities[:30]:
            sheet.append([
                opp['product'],
                opp['quality'],
                f"{opp['price_gold']:.6f}",
                opp['country'],
                f"{opp['price_local']:.2f}",
                opp['currency'],
                str(int(opp['stock'])) if opp['stock'] else "—",
                f"{opp['avg5']:.6f}" if opp['avg5'] else "—",
                f"{opp['discount_pct']:+.1f}%",
                opp['deal_rating']
            ])
        
        return sheet
    
    def _create_production_hubs_sheet(self, regions_data: List) -> List[List]:
        """Arkusz 4: Najlepsze lokalizacje produkcyjne"""
        
        sheet = [
            ["🏭 PRODUCTION HUBS - OPTIMAL MANUFACTURING LOCATIONS", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", ""],
            ["Region", "Country", "Specialization", "Regional Bonus %", "Pollution", 
             "Efficiency Score", "NPC Wages", "Investment Grade", "Recommendation"]
        ]
        
        if not regions_data:
            sheet.append(["No production data available", "", "", "", "", "", "", "", ""])
            return sheet
        
        # Przygotuj dane regionów
        production_opportunities = []
        
        for region in regions_data:
            if not isinstance(region, dict):
                continue
            
            region_name = region.get('region_name', region.get('name', 'Unknown'))
            country_name = region.get('country_name', 'Unknown')
            bonus_description = region.get('bonus_description', '')
            bonus_score = region.get('bonus_score', 0)
            pollution = region.get('pollution', 0)
            
            # Określ specjalizację
            specialization = "General"
            if bonus_description:
                if "WEAPONS:" in bonus_description:
                    specialization = "🔫 Weapons"
                elif "FOOD:" in bonus_description:
                    specialization = "🍞 Food"
                elif "GRAIN:" in bonus_description:
                    specialization = "🌾 Grain"
                elif "IRON:" in bonus_description:
                    specialization = "⚒️ Iron"
                elif "AIRCRAFT:" in bonus_description:
                    specialization = "✈️ Aircraft"
                elif "TITANIUM:" in bonus_description:
                    specialization = "🔩 Titanium"
                elif "TICKETS:" in bonus_description:
                    specialization = "🎫 Tickets"
            
            # Oblicz efektywność (bonus vs pollution)
            efficiency = bonus_score / (1 + pollution/100) if pollution > 0 else bonus_score
            
            # Szacunkowe NPC wages (potrzeba rzeczywistych danych)
            estimated_wages = max(0.5, 5.0 - efficiency/10)  # Przykładowa formuła
            
            # Ocena inwestycyjna
            if efficiency > 15 and pollution < 20:
                investment_grade = "🌟 PREMIUM"
                recommendation = "🚀 INVEST NOW"
            elif efficiency > 10 and pollution < 30:
                investment_grade = "⭐ EXCELLENT"
                recommendation = "✅ HIGHLY RECOMMENDED"
            elif efficiency > 5 and pollution < 50:
                investment_grade = "👍 GOOD"
                recommendation = "📊 CONSIDER"
            else:
                investment_grade = "⚠️ AVERAGE"
                recommendation = "🔍 RESEARCH MORE"
            
            production_opportunities.append({
                'region_name': region_name,
                'country_name': country_name,
                'specialization': specialization,
                'bonus_score': bonus_score,
                'pollution': pollution,
                'efficiency': efficiency,
                'estimated_wages': estimated_wages,
                'investment_grade': investment_grade,
                'recommendation': recommendation
            })
        
        # Sortuj według efektywności
        production_opportunities.sort(key=lambda x: x['efficiency'], reverse=True)
        
        # Dodaj top 25 regionów
        for opp in production_opportunities[:25]:
            sheet.append([
                opp['region_name'],
                opp['country_name'],
                opp['specialization'],
                f"{opp['bonus_score']:.1f}%",
                f"{opp['pollution']:.1f}%",
                f"{opp['efficiency']:.2f}",
                f"{opp['estimated_wages']:.2f}",
                opp['investment_grade'],
                opp['recommendation']
            ])
        
        return sheet
    
    def _create_economic_overview_sheet(self, country_map: Dict, currency_rates: Dict,
                                      currencies_map: Dict, regions_data: List, 
                                      best_jobs: List) -> List[List]:
        """Arkusz 5: Przegląd gospodarczy krajów"""
        
        sheet = [
            ["📊 ECONOMIC OVERVIEW - COUNTRY INVESTMENT ANALYSIS", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["Country", "Currency Strength", "Production Regions", "Avg Job Salary", 
             "Best Opportunities", "Economic Score", "Risk Level", "Investment Rating"]
        ]
        
        if not country_map:
            sheet.append(["No economic data available", "", "", "", "", "", "", ""])
            return sheet
        
        # Przygotuj analizę krajów
        country_analysis = []
        
        for country_id, country_info in country_map.items():
            if not isinstance(country_info, dict):
                continue
            
            country_name = country_info.get('name', f'Country {country_id}')
            currency_id = country_info.get('currency_id')
            
            # Siła waluty
            currency_strength = currency_rates.get(currency_id, 0)
            strength_rating = "💪 STRONG" if currency_strength > 0.3 else ("👍 MEDIUM" if currency_strength > 0.1 else "⚠️ WEAK")
            
            # Liczba regionów produkcyjnych
            production_regions = len([r for r in regions_data if isinstance(r, dict) and r.get('country_name') == country_name])
            
            # Średnia płaca w kraju
            country_jobs = [job for job in best_jobs if job.get('country_name') == country_name]
            avg_salary = sum(job.get('salary_gold', 0) for job in country_jobs) / len(country_jobs) if country_jobs else 0
            
            # Najlepsze możliwości
            opportunities_count = len(country_jobs)
            opportunities_text = f"{opportunities_count} offers" if opportunities_count > 0 else "No data"
            
            # Oblicz score ekonomiczny
            economic_score = (currency_strength * 100 + production_regions * 2 + avg_salary * 10) / 3
            
            # Poziom ryzyka
            risk_level = "🟢 LOW" if economic_score > 15 else ("🟡 MEDIUM" if economic_score > 8 else "🔴 HIGH")
            
            # Ocena inwestycyjna
            if economic_score > 20:
                investment_rating = "🌟 EXCELLENT"
            elif economic_score > 15:
                investment_rating = "⭐ VERY GOOD"
            elif economic_score > 10:
                investment_rating = "👍 GOOD"
            elif economic_score > 5:
                investment_rating = "📊 AVERAGE"
            else:
                investment_rating = "⚠️ CAUTION"
            
            country_analysis.append({
                'name': country_name,
                'currency_strength': f"{currency_strength:.4f} ({strength_rating})",
                'production_regions': production_regions,
                'avg_salary': avg_salary,
                'opportunities': opportunities_text,
                'economic_score': economic_score,
                'risk_level': risk_level,
                'investment_rating': investment_rating
            })
        
        # Sortuj według score ekonomicznego
        country_analysis.sort(key=lambda x: x['economic_score'], reverse=True)
        
        # Dodaj top 20 krajów
        for country in country_analysis[:20]:
            sheet.append([
                country['name'],
                country['currency_strength'],
                str(country['production_regions']),
                f"{country['avg_salary']:.4f}" if country['avg_salary'] > 0 else "—",
                country['opportunities'],
                f"{country['economic_score']:.1f}",
                country['risk_level'],
                country['investment_rating']
            ])
        
        return sheet
    
    def _create_investment_alerts_sheet(self, currency_rates: Dict, cheapest_items: Dict,
                                      best_jobs: List, regions_data: List, 
                                      historical_data: Dict) -> List[List]:
        """Arkusz 6: Alerty inwestycyjne i okazje arbitrażowe"""
        
        sheet = [
            ["⚡ INVESTMENT ALERTS - REAL-TIME OPPORTUNITIES", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["Alert Type", "Asset/Opportunity", "Location", "Current Value", 
             "Target Value", "Profit Potential", "Risk Level", "Action"]
        ]
        
        alerts = []
        
        # 1. Alerty walutowe (duże zmiany)
        if historical_data and currency_rates:
            yesterday_key = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            yesterday_rates = {}
            
            try:
                if yesterday_key in historical_data:
                    yesterday_rates = (historical_data[yesterday_key].get('economic_summary') or {}).get('currency_rates') or {}
            except:
                pass
            
            for currency_id, rate in currency_rates.items():
                prev_rate = yesterday_rates.get(str(currency_id))
                if prev_rate and isinstance(prev_rate, (int, float)) and prev_rate > 0:
                    change_pct = ((rate - prev_rate) / prev_rate) * 100
                    
                    if abs(change_pct) > 5:  # Zmiana > 5%
                        alert_type = "💱 CURRENCY MOVE"
                        risk = "🟡 MEDIUM" if abs(change_pct) < 10 else "🔴 HIGH"
                        action = "📈 BUY" if change_pct < -5 else "📉 SELL"
                        
                        alerts.append({
                            'type': alert_type,
                            'asset': f"Currency {currency_id}",
                            'location': "Market",
                            'current': f"{rate:.6f}",
                            'target': f"{prev_rate:.6f}",
                            'profit': f"{change_pct:+.2f}%",
                            'risk': risk,
                            'action': action
                        })
        
        # 2. Alerty rynkowe (wielkie okazje)
        if cheapest_items:
            for item_id, items_list in cheapest_items.items():
                if not items_list:
                    continue
                
                best_item = min(items_list, key=lambda x: x.get('price_gold', float('inf')))
                avg5 = best_item.get('avg5_in_gold', 0)
                price = best_item.get('price_gold', 0)
                
                if avg5 > 0:
                    discount_pct = ((avg5 - price) / avg5) * 100
                    
                    if discount_pct > 15:  # Rabat > 15%
                        alerts.append({
                            'type': "🛒 MARKET DEAL",
                            'asset': f"Item {item_id}",
                            'location': best_item.get('country', 'Unknown'),
                            'current': f"{price:.6f}",
                            'target': f"{avg5:.6f}",
                            'profit': f"{discount_pct:.1f}%",
                            'risk': "🟢 LOW",
                            'action': "🛒 BUY NOW"
                        })
        
        # 3. Alerty pracy (super oferty)
        if best_jobs:
            avg_salary = sum(job.get('salary_gold', 0) for job in best_jobs) / len(best_jobs)
            
            for job in best_jobs[:5]:  # Top 5 ofert
                salary = job.get('salary_gold', 0)
                premium = ((salary - avg_salary) / avg_salary * 100) if avg_salary > 0 else 0
                
                if premium > 50:  # Premium > 50%
                    alerts.append({
                        'type': "💼 HIGH SALARY",
                        'asset': job.get('job_title', 'Job'),
                        'location': job.get('country_name', 'Unknown'),
                        'current': f"{salary:.6f}",
                        'target': f"{avg_salary:.6f}",
                        'profit': f"{premium:.1f}%",
                        'risk': "🟢 LOW",
                        'action': "💼 APPLY"
                    })
        
        # 4. Alerty produkcyjne (super regiony)
        if regions_data:
            avg_efficiency = sum(r.get('bonus_score', 0) / (1 + r.get('pollution', 0)/100) 
                               for r in regions_data if isinstance(r, dict)) / len(regions_data)
            
            for region in regions_data:
                if not isinstance(region, dict):
                    continue
                
                bonus = region.get('bonus_score', 0)
                pollution = region.get('pollution', 0)
                efficiency = bonus / (1 + pollution/100) if pollution > 0 else bonus
                
                if efficiency > avg_efficiency * 1.5:  # 50% powyżej średniej
                    alerts.append({
                        'type': "🏭 PRODUCTION HOT",
                        'asset': region.get('region_name', 'Region'),
                        'location': region.get('country_name', 'Unknown'),
                        'current': f"{efficiency:.2f}",
                        'target': f"{avg_efficiency:.2f}",
                        'profit': f"{((efficiency - avg_efficiency) / avg_efficiency * 100):+.1f}%",
                        'risk': "🟡 MEDIUM",
                        'action': "🏭 INVEST"
                    })
        
        # Sortuj alerty według potencjału zysku
        alerts.sort(key=lambda x: float(x['profit'].replace('%', '').replace('+', '')), reverse=True)
        
        # Dodaj alerty do arkusza (top 20)
        for alert in alerts[:20]:
            sheet.append([
                alert['type'],
                alert['asset'],
                alert['location'],
                alert['current'],
                alert['target'],
                alert['profit'],
                alert['risk'],
                alert['action']
            ])
        
        if not alerts:
            sheet.append(["No active alerts", "Monitor markets", "—", "—", "—", "—", "🟢 LOW", "⏰ WAIT"])
        
        return sheet
