#!/usr/bin/env python
"""
Load CSS from file into CTFd database during startup
"""
import os
from CTFd import create_app
from CTFd.models import db, Configs
from CTFd.utils import set_config

def load_css():
    """Load cybermeister CSS, header and footer into the database"""
    app = create_app()
    
    with app.app_context():
        header_file = "CTFd/themes/core/static/css/cybermeister-header.html"
        footer_file = "CTFd/themes/core/static/css/cybermeister-footer.html"
        
        # Read header
        if not os.path.exists(header_file):
            print(f"[ WARNING ] Header file not found: {header_file}")
            return
        
        with open(header_file, 'r', encoding='utf-8') as f:
            header_content = f.read()
        
        # Read footer
        if not os.path.exists(footer_file):
            print(f"[ WARNING ] Footer file not found: {footer_file}")
            return
        
        with open(footer_file, 'r', encoding='utf-8') as f:
            footer_content = f.read()
        
        try:
            # Use set_config to properly update and clear cache
            set_config("theme_header", header_content)
            print(f"[ SUCCESS ] theme_header loaded into database")
            
            set_config("theme_footer", footer_content)
            print(f"[ SUCCESS ] theme_footer loaded into database")
            
        except Exception as e:
            print(f"[ ERROR ] Failed to load header/footer: {e}")
            raise
if __name__ == "__main__":
    load_css()
