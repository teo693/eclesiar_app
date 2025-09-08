#!/usr/bin/env python3
"""
Convert HTML report to Markdown format for easy copying
"""

from bs4 import BeautifulSoup
import re
from datetime import datetime

def html_to_markdown(html_file_path, output_file_path):
    """Convert HTML report to Markdown format"""
    
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    markdown_content = ""
    
    # Extract title
    title = soup.find('title')
    if title:
        markdown_content += f"# {title.get_text()}\n\n"
    
    # Process sections
    sections = soup.find_all('div', class_='section')
    
    for section in sections:
        # Section headers (h2)
        h2 = section.find('h2')
        if h2:
            section_title = h2.get_text()
            markdown_content += f"## {section_title}\n\n"
        
        # Subsection headers (h3)
        h3s = section.find_all('h3')
        for h3 in h3s:
            subsection_title = h3.get_text()
            markdown_content += f"### {subsection_title}\n\n"
            
            # Find table directly after this h3 (not in category section)
            current = h3.next_sibling
            next_table = None
            
            while current:
                if hasattr(current, 'name'):
                    if current.name == 'table':
                        next_table = current
                        break
                    elif current.name in ['h3', 'h2', 'h1']:
                        break  # Stop if we hit another header
                current = current.next_sibling
            
            if next_table:
                    # Table headers
                    headers = next_table.find_all('th')
                    if headers:
                        header_row = "| " + " | ".join([th.get_text().strip() for th in headers]) + " |"
                        separator_row = "|" + "|".join(["---" for _ in headers]) + "|"
                        markdown_content += header_row + "\n"
                        markdown_content += separator_row + "\n"
                    
                    # Table rows
                    rows = next_table.find_all('tr')[1:]  # Skip header row
                    for row in rows:
                        cells = row.find_all('td')
                        if cells:
                            row_data = "| " + " | ".join([td.get_text().strip() for td in cells]) + " |"
                            markdown_content += row_data + "\n"
                    
                    markdown_content += "\n"
        
        # Category sections (h4)
        h4s = section.find_all('h4', class_='category-title')
        for h4 in h4s:
            category_title = h4.get_text()
            markdown_content += f"#### {category_title}\n\n"
            
            # Find table after this h4
            next_table = h4.find_next('table')
            if next_table:
                # Table headers
                headers = next_table.find_all('th')
                if headers:
                    header_row = "| " + " | ".join([th.get_text().strip() for th in headers]) + " |"
                    separator_row = "|" + "|".join(["---" for _ in headers]) + "|"
                    markdown_content += header_row + "\n"
                    markdown_content += separator_row + "\n"
                
                # Table rows
                rows = next_table.find_all('tr')[1:]  # Skip header row
                for row in rows:
                    cells = row.find_all('td')
                    if cells:
                        row_data = "| " + " | ".join([td.get_text().strip() for td in cells]) + " |"
                        markdown_content += row_data + "\n"
                
                markdown_content += "\n"
        
        # Tables not in category sections
        tables = section.find_all('table')
        for table in tables:
            # Skip if already processed as part of category
            prev_h4 = table.find_previous('h4', class_='category-title')
            if prev_h4:
                # Check if h4 is within same section as the table
                if prev_h4.find_parent('div', class_='section') == section:
                    continue
                
            # Table headers
            headers = table.find_all('th')
            if headers:
                header_row = "| " + " | ".join([th.get_text().strip() for th in headers]) + " |"
                separator_row = "|" + "|".join(["---" for _ in headers]) + "|"
                markdown_content += header_row + "\n"
                markdown_content += separator_row + "\n"
            
            # Table rows
            rows = table.find_all('tr')[1:]  # Skip header row
            for row in rows:
                cells = row.find_all('td')
                if cells:
                    row_data = "| " + " | ".join([td.get_text().strip() for td in cells]) + " |"
                    markdown_content += row_data + "\n"
            
            markdown_content += "\n"
        
        # Regular paragraphs
        paragraphs = section.find_all('p')
        for p in paragraphs:
            p_text = p.get_text().strip()
            if p_text and not p.find_parent('table'):  # Skip paragraphs inside tables
                markdown_content += f"{p_text}\n\n"
        
        # Lists
        lists = section.find_all('ul')
        for ul in lists:
            items = ul.find_all('li')
            for li in items:
                li_text = li.get_text().strip()
                markdown_content += f"- {li_text}\n"
            markdown_content += "\n"
        
        markdown_content += "\n"
    
    # Write Markdown file
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"Markdown file generated: {output_file_path}")
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
    
    md_path = html_path.replace('.html', '.md')
    
    html_to_markdown(html_path, md_path)

