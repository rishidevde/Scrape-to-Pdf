"""
Professional PDF Generator from Crawled Website Data
Generates PDF reports that look like website screenshots
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List
import logging
from io import BytesIO

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, 
    Table, TableStyle, KeepTogether, Preformatted
)
from PIL import Image as PILImage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProfessionalPDFGenerator:
    """Generate professional PDF from crawled website data"""
    
    def __init__(self, data_dir: str = "crawled_data", output_pdf: Optional[str] = None):
        """
        Initialize PDF generator
        
        Args:
            data_dir: Directory containing crawled data
            output_pdf: Output PDF filename (auto-generated if None)
        """
        self.data_dir = data_dir
        self.images_dir = os.path.join(data_dir, "images")
        self.json_file = os.path.join(data_dir, "crawled_data.json")
        
        # Load data
        self.data = self._load_json_data()
        
        # Generate output filename if not provided
        if output_pdf is None:
            domain = self.data.get('metadata', {}).get('base_url', 'website').split('//')[1].split('/')[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_pdf = f"{domain}_{timestamp}.pdf"
        
        self.output_pdf = output_pdf
        
        # Create PDF document
        self.doc = SimpleDocTemplate(
            output_pdf,
            pagesize=A4,
            rightMargin=0.6*inch,
            leftMargin=0.6*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
            title="Website Crawl Report"
        )
        
        self.story = []
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _load_json_data(self) -> dict:
        """Load crawled data from JSON"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON: {e}")
            return {}
    
    def _create_custom_styles(self):
        """Create professional custom styles"""
        # Main title
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=32,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=38
        ))
        
        # Subtitle
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#666666'),
            spaceAfter=24,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHead',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#FFFFFF'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#1a5490'),
            borderColor=colors.HexColor('#1a5490'),
            borderWidth=1,
            borderPadding=8,
            leftIndent=8
        ))
        
        # Subsection heading
        self.styles.add(ParagraphStyle(
            name='SubsectionHead',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=8,
            spaceBefore=8,
            fontName='Helvetica-Bold',
            borderColor=colors.HexColor('#1a5490'),
            borderWidth=0,
            borderBottomWidth=2,
            borderPadding=6
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=self.styles['BodyText'],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            fontName='Helvetica'
        ))
        
        # Contact info
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            fontName='Helvetica',
            leftIndent=12
        ))
        
        # Metadata
        self.styles.add(ParagraphStyle(
            name='Metadata',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#888888'),
            spaceAfter=4,
            fontName='Helvetica'
        ))
        
        # Link text
        self.styles.add(ParagraphStyle(
            name='LinkText',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=4,
            fontName='Helvetica',
            leftIndent=12
        ))
    
    def _get_image_size(self, image_path: str, max_width: float = 6*inch, max_height: float = 4*inch) -> Tuple[float, float]:
        """Calculate appropriate image size maintaining aspect ratio"""
        try:
            img = PILImage.open(image_path)
            img_width, img_height = img.size
            
            if img_width == 0 or img_height == 0:
                return 4*inch, 3*inch
            
            ratio = img_width / img_height
            
            if img_width > max_width or img_height > max_height:
                if ratio > max_width / max_height:
                    width = max_width
                    height = max_width / ratio
                else:
                    height = max_height
                    width = max_height * ratio
            else:
                width = img_width * 0.35
                height = img_height * 0.35
            
            return width, height
        except Exception as e:
            logger.warning(f"Error getting image size: {e}")
            return 4*inch, 3*inch
    
    def add_title_page(self):
        """Add professional title page"""
        self.story.append(Spacer(1, 1*inch))
        
        # Main title
        base_url = self.data.get('metadata', {}).get('base_url', 'Website')
        domain = base_url.split('//')[1].split('/')[0] if '//' in base_url else base_url
        
        title = Paragraph(
            domain.upper(),
            self.styles['MainTitle']
        )
        self.story.append(title)
        
        self.story.append(Spacer(1, 0.3*inch))
        
        # Subtitle
        subtitle = Paragraph(
            "Website Crawl Report & Data Extract",
            self.styles['Subtitle']
        )
        self.story.append(subtitle)
        
        self.story.append(Spacer(1, 0.5*inch))
        
        # Metadata box
        metadata = self.data.get('metadata', {})
        main_page = self.data.get('main_page', {})
        page_meta = main_page.get('metadata', {})
        
        info_text = f"""
        <b>Website Title:</b> {page_meta.get('title', 'N/A')}<br/>
        <b>URL:</b> {metadata.get('base_url', 'N/A')}<br/>
        <b>Description:</b> {page_meta.get('description', 'No description available')[:100]}<br/>
        <b>Pages Crawled:</b> {metadata.get('pages_crawled', 1)}<br/>
        <b>Crawled:</b> {metadata.get('crawl_time', 'N/A')[:10]}<br/>
        <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        """
        
        self.story.append(Paragraph(info_text, self.styles['Metadata']))
        
        self.story.append(Spacer(1, 0.8*inch))
        
        # Statistics box
        stats_text = f"""
        <b>Statistics:</b><br/>
        Total Images: {metadata.get('total_images', 0)} | 
        Total Links: {metadata.get('total_links', 0)} |
        Emails: {metadata.get('total_emails', 0)} |
        Phones: {metadata.get('total_phones', 0)}
        """
        
        self.story.append(Paragraph(stats_text, self.styles['CustomBodyText']))
        
        self.story.append(PageBreak())
    
    def add_table_of_contents(self):
        """Add table of contents"""
        self.story.append(Paragraph("TABLE OF CONTENTS", self.styles['SectionHead']))
        self.story.append(Spacer(1, 0.2*inch))
        
        toc_items = [
            "1. Website Overview & Contact Information",
            "2. Website Content Sections",
            "3. Extracted Data Tables",
            "4. Complete Links Directory",
            "5. Image Gallery",
            "6. Additional Pages",
            "7. Summary & Statistics"
        ]
        
        for item in toc_items:
            self.story.append(Paragraph(
                item,
                ParagraphStyle(
                    name='TOC_Item',
                    parent=self.styles['Normal'],
                    fontSize=11,
                    spaceAfter=6,
                    leftIndent=20,
                    textColor=colors.HexColor('#1a5490')
                )
            ))
        
        self.story.append(PageBreak())
    
    def add_overview_section(self):
        """Add website overview"""
        self.story.append(Paragraph("WEBSITE OVERVIEW & CONTACT INFORMATION", self.styles['SectionHead']))
        self.story.append(Spacer(1, 0.2*inch))
        
        main_page = self.data.get('main_page', {})
        metadata = main_page.get('metadata', {})
        
        # Basic info
        info_items = [
            f"<b>Website Title:</b> {metadata.get('title', 'N/A')}",
            f"<b>URL:</b> {metadata.get('url', 'N/A')}",
            f"<b>Description:</b> {metadata.get('description', 'N/A')}",
            f"<b>Keywords:</b> {metadata.get('keywords', 'N/A')}"
        ]
        
        for item in info_items:
            self.story.append(Paragraph(item, self.styles['CustomBodyText']))
            self.story.append(Spacer(1, 0.05*inch))
        
        # Contact information
        self.story.append(Spacer(1, 0.2*inch))
        self.story.append(Paragraph("CONTACT INFORMATION", self.styles['SubsectionHead']))
        
        contact = main_page.get('contact_info', {})
        
        # Emails
        if contact.get('emails'):
            self.story.append(Paragraph("<b>Email Addresses:</b>", self.styles['CustomBodyText']))
            for email in contact['emails']:
                self.story.append(Paragraph(f"• {email}", self.styles['ContactInfo']))
            self.story.append(Spacer(1, 0.1*inch))
        
        # Phones
        if contact.get('phones'):
            self.story.append(Paragraph("<b>Phone Numbers:</b>", self.styles['CustomBodyText']))
            for phone in contact['phones']:
                self.story.append(Paragraph(f"• {phone}", self.styles['ContactInfo']))
            self.story.append(Spacer(1, 0.1*inch))
        
        # Addresses
        if contact.get('addresses'):
            self.story.append(Paragraph("<b>Addresses:</b>", self.styles['CustomBodyText']))
            for address in contact['addresses']:
                self.story.append(Paragraph(f"• {address}", self.styles['ContactInfo']))
        
        self.story.append(PageBreak())
    
    def add_content_sections(self):
        """Add main content sections"""
        main_page = self.data.get('main_page', {})
        sections = main_page.get('sections', {})
        
        if not sections:
            return
        
        self.story.append(Paragraph("WEBSITE CONTENT SECTIONS", self.styles['SectionHead']))
        self.story.append(Spacer(1, 0.15*inch))
        
        for section_name, content_items in sections.items():
            if not content_items:
                continue
            
            self.story.append(Paragraph(
                section_name.replace('_', ' ').title(),
                self.styles['SubsectionHead']
            ))
            
            # Add limited content
            for item in content_items[:8]:
                if isinstance(item, str) and len(item) > 0:
                    self.story.append(Paragraph(item[:200], self.styles['CustomBodyText']))
            
            self.story.append(Spacer(1, 0.15*inch))
        
        self.story.append(PageBreak())
    
    def add_tables_section(self):
        """Add extracted tables"""
        main_page = self.data.get('main_page', {})
        tables = main_page.get('tables', [])
        
        if not tables:
            return
        
        self.story.append(Paragraph("EXTRACTED DATA TABLES", self.styles['SectionHead']))
        self.story.append(Spacer(1, 0.15*inch))
        
        for table_data in tables[:3]:  # Limit to 3 tables
            self.story.append(Paragraph(
                f"Table {table_data['table_number']}",
                self.styles['SubsectionHead']
            ))
            self.story.append(Spacer(1, 0.1*inch))
            
            # Create table
            headers = table_data.get('headers', [])
            rows = table_data.get('rows', [])
            
            if headers or rows:
                table_content = [headers] if headers else []
                table_content.extend(rows[:10])  # Limit rows
                
                # Calculate column widths
                num_cols = len(headers) if headers else (len(rows[0]) if rows else 1)
                col_width = 7.2 / num_cols
                
                tbl = Table(table_content, colWidths=[col_width*inch]*num_cols)
                tbl.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
                ]))
                
                self.story.append(tbl)
                self.story.append(Spacer(1, 0.2*inch))
        
        self.story.append(PageBreak())
    
    def add_links_directory(self):
        """Add links directory"""
        all_links = self.data.get('all_links', [])
        
        if not all_links:
            return
        
        self.story.append(Paragraph("COMPLETE LINKS DIRECTORY", self.styles['SectionHead']))
        self.story.append(Spacer(1, 0.15*inch))
        
        # Create links table
        link_data = [['#', 'Link Text', 'URL']]
        
        for idx, link in enumerate(all_links[:60], 1):  # Limit to 60
            text = link.get('text', 'N/A')[:25]
            url = link.get('url', 'N/A')[:35]
            link_data.append([str(idx), text, url])
        
        link_table = Table(link_data, colWidths=[0.5*inch, 2.2*inch, 3.5*inch])
        link_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 7.5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
        ]))
        
        self.story.append(link_table)
        
        if len(all_links) > 60:
            self.story.append(Spacer(1, 0.1*inch))
            self.story.append(Paragraph(
                f"... and {len(all_links) - 60} more links (see JSON file)",
                self.styles['Metadata']
            ))
        
        self.story.append(PageBreak())
    
    def add_image_gallery(self):
        """Add image gallery"""
        if not os.path.exists(self.images_dir):
            return
        
        image_files = [f for f in os.listdir(self.images_dir)
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
        
        if not image_files:
            return
        
        self.story.append(Paragraph("IMAGE GALLERY", self.styles['SectionHead']))
        self.story.append(Spacer(1, 0.15*inch))
        
        self.story.append(Paragraph(
            f"Total Images: {len(image_files)}",
            self.styles['CustomBodyText']
        ))
        self.story.append(Spacer(1, 0.1*inch))
        
        # Add images
        images_added = 0
        for image_file in sorted(image_files):
            if images_added >= 40:  # Limit to 40 images
                self.story.append(Paragraph(
                    f"... and {len(image_files) - 40} more images",
                    self.styles['Metadata']
                ))
                break
            
            image_path = os.path.join(self.images_dir, image_file)
            
            try:
                width, height = self._get_image_size(image_path, 3.5*inch, 2.5*inch)
                img = Image(image_path, width=width, height=height)
                
                self.story.append(Paragraph(
                    f"<b>{image_file[:40]}</b>",
                    ParagraphStyle(
                        name='ImgCaption',
                        parent=self.styles['Normal'],
                        fontSize=8,
                        fontName='Helvetica'
                    )
                ))
                self.story.append(img)
                self.story.append(Spacer(1, 0.15*inch))
                
                images_added += 1
                
                if images_added % 3 == 0:
                    self.story.append(PageBreak())
                    self.story.append(Spacer(1, 0.1*inch))
                    
            except Exception as e:
                logger.warning(f"Error adding image {image_file}: {e}")
                continue
    
    def add_additional_pages(self):
        """Add information about additional crawled pages"""
        pages = self.data.get('pages', [])
        
        if not pages:
            return
        
        self.story.append(PageBreak())
        self.story.append(Paragraph("ADDITIONAL PAGES", self.styles['SectionHead']))
        self.story.append(Spacer(1, 0.15*inch))
        
        self.story.append(Paragraph(
            f"Total Additional Pages Crawled: {len(pages)}",
            self.styles['CustomBodyText']
        ))
        self.story.append(Spacer(1, 0.15*inch))
        
        for idx, page in enumerate(pages[:10], 1):  # Show first 10
            page_meta = page.get('metadata', {})
            
            page_info = f"""
            <b>Page {idx}:</b> {page_meta.get('title', 'Untitled')}<br/>
            <b>URL:</b> {page_meta.get('url', 'N/A')[:80]}<br/>
            <b>Links:</b> {len(page.get('links', []))} | 
            <b>Images:</b> {len(page.get('images', []))}
            """
            
            self.story.append(Paragraph(page_info, self.styles['CustomBodyText']))
            self.story.append(Spacer(1, 0.1*inch))
    
    def add_summary(self):
        """Add final summary"""
        self.story.append(PageBreak())
        self.story.append(Paragraph("SUMMARY & STATISTICS", self.styles['SectionHead']))
        self.story.append(Spacer(1, 0.15*inch))
        
        metadata = self.data.get('metadata', {})
        all_emails = self.data.get('all_emails', [])
        all_phones = self.data.get('all_phones', [])
        
        summary_text = f"""
        <b>Crawl Statistics:</b><br/>
        • Pages Crawled: {metadata.get('pages_crawled', 0)}<br/>
        • Total Links Found: {metadata.get('total_links', 0)}<br/>
        • Total Images Found: {metadata.get('total_images', 0)}<br/>
        • Unique Emails: {len(all_emails)}<br/>
        • Unique Phone Numbers: {len(all_phones)}<br/>
        <br/>
        <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Report Format:</b> Professional PDF Export<br/>
        <b>Data Source:</b> {metadata.get('base_url', 'N/A')}<br/>
        """
        
        self.story.append(Paragraph(summary_text, self.styles['CustomBodyText']))
        
        self.story.append(Spacer(1, 0.3*inch))
        
        footer_text = "This report was automatically generated by Website Crawler. All data is extracted programmatically."
        self.story.append(Paragraph(
            footer_text,
            ParagraphStyle(
                name='Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#999999'),
                alignment=TA_CENTER
            )
        ))
    
    def generate(self) -> bool:
        """Generate the complete PDF"""
        print(f"\n{'='*80}")
        print("PDF Generation Starting")
        print(f"{'='*80}\n")
        
        try:
            if not self.data:
                logger.error("No data loaded")
                return False
            
            print("[*] Adding title page...")
            self.add_title_page()
            
            print("[*] Adding table of contents...")
            self.add_table_of_contents()
            
            print("[*] Adding overview section...")
            self.add_overview_section()
            
            print("[*] Adding content sections...")
            self.add_content_sections()
            
            print("[*] Adding tables...")
            self.add_tables_section()
            
            print("[*] Adding links directory...")
            self.add_links_directory()
            
            print("[*] Adding image gallery...")
            self.add_image_gallery()
            
            print("[*] Adding additional pages info...")
            self.add_additional_pages()
            
            print("[*] Adding summary...")
            self.add_summary()
            
            # Build PDF
            print(f"[*] Building PDF: {self.output_pdf}")
            self.doc.build(self.story)
            
            # Get file size
            if os.path.exists(self.output_pdf):
                file_size = os.path.getsize(self.output_pdf) / (1024 * 1024)
                print(f"\n[+] PDF generated successfully!")
                print(f"[+] File: {self.output_pdf}")
                print(f"[+] Size: {file_size:.2f} MB")
                print(f"[+] Pages: ~{len(self.story) // 10}")  # Rough estimate
                return True
            else:
                logger.error("PDF file not created")
                return False
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("PROFESSIONAL PDF REPORT GENERATOR")
    print("="*80 + "\n")
    
    data_dir = "crawled_data"
    
    if not os.path.exists(os.path.join(data_dir, "crawled_data.json")):
        print(f"[-] Error: No crawled_data.json found in {data_dir}")
        print("[*] Please run web_crawler.py first")
        sys.exit(1)
    
    generator = ProfessionalPDFGenerator(data_dir)
    
    if generator.generate():
        print("\n[+] PDF Report ready!")
        print(f"[+] Open: {generator.output_pdf}")
    else:
        print("\n[-] PDF generation failed")
        sys.exit(1)


if __name__ == "__main__":
    import sys
    main()
