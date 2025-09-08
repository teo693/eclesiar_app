#!/usr/bin/env python3
"""
Generate all text export formats from the latest HTML report
"""

import os
import sys
from export_markdown import html_to_markdown
from export_plaintext import html_to_plaintext

def export_all_formats():
    """Export latest HTML report to all text formats"""
    
    # Find latest HTML report
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        print("Reports directory not found!")
        return
    
    html_files = [f for f in os.listdir(reports_dir) if f.endswith('.html')]
    if not html_files:
        print("No HTML reports found!")
        return
    
    latest_html = max(html_files, key=lambda x: os.path.getctime(os.path.join(reports_dir, x)))
    html_path = os.path.join(reports_dir, latest_html)
    
    print(f"🔄 Converting latest report: {latest_html}")
    print()
    
    # Generate Markdown
    md_path = html_path.replace('.html', '.md')
    html_to_markdown(html_path, md_path)
    
    # Generate Plain Text
    txt_path = html_path.replace('.html', '.txt')
    html_to_plaintext(html_path, txt_path)
    
    print()
    print("✅ Export complete! Generated files:")
    print(f"   📝 Markdown: {md_path}")
    print(f"   📄 Plain Text: {txt_path}")
    print()
    print("💡 Recommendations for text editors:")
    print("   • Notepad++: Open .md file (best Unicode support)")
    print("   • Notepad: Open .txt file")
    print("   • WordPad: Open .md file (preserves formatting)")
    print("   • VS Code: Open .md file (with preview)")
    print()
    print("🎯 For best results in Notepad:")
    print(f"   1. Open: {txt_path}")
    print("   2. Set font to: Consolas or Courier New")
    print("   3. Unicode icons will display properly")

if __name__ == "__main__":
    export_all_formats()

