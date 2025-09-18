"""
Google Sheets Report Exporter

Copyright (c) 2025 Teo693
Licensed under the MIT License - see LICENSE file for details.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from .sheets_auth import GoogleSheetsAuth
from .sheets_formatter import SheetsFormatter
from ..factories.report_factory import ReportGenerator
from ...core.models.entities import ReportType
from ...core.services.base_service import ServiceDependencies
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from config.settings.google_sheets import GOOGLE_SHEETS_EXISTING_ID

class GoogleSheetsExporter(ReportGenerator):
    """Google Sheets report generator"""
    
    def __init__(self, dependencies: ServiceDependencies):
        super().__init__(dependencies)
        self.auth = GoogleSheetsAuth()
        self.formatter = SheetsFormatter()
    
    def generate(self, data: Dict[str, Any], sections: Dict[str, bool], 
                output_dir: str) -> Optional[str]:
        """Generate Google Sheets report"""
        try:
            print("🔄 Generating Google Sheets report...")
            
            # Authenticate with Google Sheets
            service = self.auth.authenticate()
            drive_service = self.auth.get_drive_service()
            
            # Determine report type and format data
            report_type = self._determine_report_type(data)
            formatted_data = self._format_data_by_type(data, report_type)
            
            # Use existing spreadsheet or create new one
            if GOOGLE_SHEETS_EXISTING_ID:
                print(f"📊 Using existing spreadsheet: {GOOGLE_SHEETS_EXISTING_ID}")
                spreadsheet_id = GOOGLE_SHEETS_EXISTING_ID
                try:
                    # Update existing spreadsheet
                    self._update_existing_spreadsheet(spreadsheet_id, formatted_data, service)
                except Exception as update_error:
                    print(f"⚠️ Failed to update existing spreadsheet: {update_error}")
                    print("🔄 Creating new spreadsheet instead...")
                    # Fallback: create new spreadsheet if update fails
                    spreadsheet_id = self._create_spreadsheet(formatted_data, report_type, service)
                    self._share_spreadsheet(spreadsheet_id, drive_service)
            else:
                # Create new spreadsheet
                spreadsheet_id = self._create_spreadsheet(formatted_data, report_type, service)
                # Share spreadsheet (optional)
                self._share_spreadsheet(spreadsheet_id, drive_service)
            
            # Get spreadsheet URL
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            
            print(f"✅ Google Sheets report created: {spreadsheet_url}")
            return spreadsheet_url
            
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg and "permission" in error_msg.lower():
                print("❌ Error generating Google Sheets report: Permission denied")
                print("🔧 To fix this issue:")
                print("   1. Go to Google Cloud Console (https://console.cloud.google.com/)")
                print("   2. Select your project")
                print("   3. Go to IAM & Admin > IAM")
                print("   4. Find your service account")
                print("   5. Add the following roles:")
                print("      - Google Sheets API > Editor")
                print("      - Google Drive API > Editor")
                print("   6. Enable Google Sheets API and Google Drive API in the APIs & Services section")
                print("   7. Wait a few minutes for permissions to propagate")
            else:
                print(f"❌ Error generating Google Sheets report: {e}")
            return None
    
    def _determine_report_type(self, data: Dict[str, Any]) -> str:
        """Determine report type based on data content"""
        # Sprawdź czy to raport ekonomiczny (ma currency_rates ale nie ma military/warriors)
        if 'currency_rates' in data and (not data.get('military_summary') or not data.get('top_warriors')):
            return 'economic'
        # Dla innych przypadków używaj format_daily_report
        return 'daily'
    
    def _format_data_by_type(self, data: Dict[str, Any], report_type: str) -> Dict[str, List[List]]:
        """Format data based on report type"""
        if report_type == 'production':
            return self.formatter.format_production_report(data)
        elif report_type == 'economic':
            return self.formatter.format_economic_report(data)
        else:
            return self.formatter.format_daily_report(data)
    
    def _create_spreadsheet(self, formatted_data: Dict[str, List[List]], 
                           report_type: str, service) -> str:
        """Create Google Sheets spreadsheet"""
        
        # Create spreadsheet
        spreadsheet_body = {
            'properties': {
                'title': f"Eclesiar Report - {report_type.title()} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            },
            'sheets': []
        }
        
        # Add sheets
        for sheet_name, sheet_data in formatted_data.items():
            sheet = {
                'properties': {
                    'title': sheet_name,
                    'gridProperties': {
                        'rowCount': len(sheet_data),
                        'columnCount': max(len(row) for row in sheet_data) if sheet_data else 1
                    }
                },
                'data': [{
                    'rowData': [{'values': [{'userEnteredValue': {'stringValue': str(cell)} for cell in row}] 
                               for row in sheet_data}]
                }]
            }
            spreadsheet_body['sheets'].append(sheet)
        
        # Create the spreadsheet
        spreadsheet = service.spreadsheets().create(body=spreadsheet_body).execute()
        spreadsheet_id = spreadsheet['spreadsheetId']
        
        # Format the spreadsheet
        self._format_spreadsheet(spreadsheet_id, service)
        
        return spreadsheet_id
    
    def _update_existing_spreadsheet(self, spreadsheet_id: str, formatted_data: Dict[str, List[List]], service) -> None:
        """Update existing spreadsheet with new data"""
        try:
            # Get existing spreadsheet info
            spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            print(f"📊 Updating existing spreadsheet: {spreadsheet['properties']['title']}")
            
            # Clear existing data and add new data
            for sheet_name, sheet_data in formatted_data.items():
                # Find or create sheet
                sheet_id = self._find_or_create_sheet(spreadsheet_id, sheet_name, service)
                
                # Clear existing data in the sheet
                self._clear_sheet_data(spreadsheet_id, sheet_id, service)
                
                # Add new data
                if sheet_data:
                    self._add_data_to_sheet(spreadsheet_id, sheet_id, sheet_data, service)
            
            # Apply formatting
            self._format_spreadsheet(spreadsheet_id, service)
            
        except Exception as e:
            print(f"⚠️ Warning: Could not update existing spreadsheet: {e}")
            raise e
    
    def _find_or_create_sheet(self, spreadsheet_id: str, sheet_name: str, service) -> int:
        """Find existing sheet or create new one"""
        try:
            spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            
            # Look for existing sheet
            for sheet in spreadsheet['sheets']:
                if sheet['properties']['title'] == sheet_name:
                    return sheet['properties']['sheetId']
            
            # Create new sheet if not found
            requests = [{
                'addSheet': {
                    'properties': {
                        'title': sheet_name
                    }
                }
            }]
            
            body = {'requests': requests}
            result = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            return result['replies'][0]['addSheet']['properties']['sheetId']
            
        except Exception as e:
            print(f"⚠️ Warning: Could not find/create sheet {sheet_name}: {e}")
            return 0  # Use first sheet as fallback
    
    def _clear_sheet_data(self, spreadsheet_id: str, sheet_id: int, service) -> None:
        """Clear all data in a sheet"""
        try:
            # Get sheet range
            spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheet = next(s for s in spreadsheet['sheets'] if s['properties']['sheetId'] == sheet_id)
            sheet_name = sheet['properties']['title']
            
            # Clear the sheet
            service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A:Z"
            ).execute()
            
        except Exception as e:
            print(f"⚠️ Warning: Could not clear sheet data: {e}")
    
    def _add_data_to_sheet(self, spreadsheet_id: str, sheet_id: int, sheet_data: List[List], service) -> None:
        """Add data to a specific sheet"""
        try:
            # Get sheet name
            spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheet = next(s for s in spreadsheet['sheets'] if s['properties']['sheetId'] == sheet_id)
            sheet_name = sheet['properties']['title']
            
            print(f"📊 Adding {len(sheet_data)} rows to sheet '{sheet_name}'")
            if sheet_data:
                print(f"   First row: {sheet_data[0]}")
            
            # Add data
            body = {'values': sheet_data}
            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A1",
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"✅ Successfully updated {result.get('updatedCells', 0)} cells in sheet '{sheet_name}'")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not add data to sheet: {e}")
            import traceback
            traceback.print_exc()
    
    def _format_spreadsheet(self, spreadsheet_id: str, service) -> None:
        """Apply formatting to the spreadsheet"""
        try:
            # Get sheet properties
            spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            
            # Format headers (first row of each sheet)
            requests = []
            for sheet in spreadsheet['sheets']:
                sheet_id = sheet['properties']['sheetId']
                sheet_name = sheet['properties']['title']
                
                # Format header row
                requests.append({
                    'repeatCell': {
                        'range': {
                            'sheetId': sheet_id,
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
                                'textFormat': {
                                    'foregroundColor': {'red': 1, 'green': 1, 'blue': 1},
                                    'bold': True
                                }
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                })
            
            # Apply formatting
            if requests:
                body = {'requests': requests}
                service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id, 
                    body=body
                ).execute()
                
        except Exception as e:
            print(f"⚠️ Warning: Could not apply formatting: {e}")
    
    def _share_spreadsheet(self, spreadsheet_id: str, drive_service) -> None:
        """Share spreadsheet with users (optional)"""
        try:
            # Get spreadsheet info
            spreadsheet = drive_service.files().get(fileId=spreadsheet_id).execute()
            
            # Make it viewable by anyone with the link
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            drive_service.permissions().create(
                fileId=spreadsheet_id,
                body=permission
            ).execute()
            
            print(f"📤 Spreadsheet shared: {spreadsheet['webViewLink']}")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not share spreadsheet: {e}")
    
    def get_report_type(self) -> ReportType:
        return ReportType.GOOGLE_SHEETS
