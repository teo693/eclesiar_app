#!/usr/bin/env python3
"""
Convert HTML report to RTF format for easy copying to text editors
"""

from bs4 import BeautifulSoup
import re
from datetime import datetime

def html_to_rtf(html_file_path, output_file_path):
    """Convert HTML report to RTF format"""
    
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    rtf_content = r"""{\rtf1\ansi\deff0 
{\fonttbl{\f0 Times New Roman;}{\f1 Courier New;}}
{\colortbl;\red0\green0\blue0;\red255\green0\blue0;\red0\green128\blue0;\red255\green165\blue0;}
"""
    
    # Extract title
    title = soup.find('title')
    if title:
        rtf_content += r"\f0\fs28\b " + title.get_text() + r"\b0\fs20\par\par"
    
    # Process sections
    sections = soup.find_all('div', class_='section')
    
    for section in sections:
        # Section headers (h2)
        h2 = section.find('h2')
        if h2:
            section_title = h2.get_text()
            rtf_content += r"\f0\fs24\b " + section_title + r"\b0\fs20\par\par"
        
        # Subsection headers (h3)
        h3s = section.find_all('h3')
        for h3 in h3s:
            subsection_title = h3.get_text()
            rtf_content += r"\f0\fs22\b " + subsection_title + r"\b0\fs20\par\par"
        
        # Tables
        tables = section.find_all('table')
        for table in tables:
            # Table headers
            headers = table.find_all('th')
            if headers:
                header_text = " | ".join([th.get_text().strip() for th in headers])
                rtf_content += r"\f1\b " + header_text + r"\b0\par"
                rtf_content += "-" * len(header_text) + r"\par"
            
            # Table rows
            rows = table.find_all('tr')[1:]  # Skip header row
            for row in rows:
                cells = row.find_all('td')
                if cells:
                    row_text = " | ".join([td.get_text().strip() for td in cells])
                    rtf_content += r"\f1 " + row_text + r"\par"
            
            rtf_content += r"\par"
        
        # Regular paragraphs
        paragraphs = section.find_all('p')
        for p in paragraphs:
            p_text = p.get_text().strip()
            if p_text:
                rtf_content += r"\f0 " + p_text + r"\par\par"
        
        rtf_content += r"\par"
    
    rtf_content += "}"
    
    # Write RTF file
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(rtf_content)
    
    print(f"RTF file generated: {output_file_path}")
    return output_file_path

if __name__ == "__main__":
    import sys
    import os
    
    # Find latest HTML report
    reports_dir = "reports"
    html_files = [f for f in os.listdir(reports_dir) if f.endswith('.html')]
    if not html_files:
        print("No HTML reports found!")
        sys.exit(1)
    
    latest_html = max(html_files, key=lambda x: os.path.getctime(os.path.join(reports_dir, x)))
    html_path = os.path.join(reports_dir, latest_html)
    
    rtf_path = html_path.replace('.html', '.rtf')
    
    html_to_rtf(html_path, rtf_path)

