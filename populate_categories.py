import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartITSupport.settings')
django.setup()

from tickets.models import Category, SubCategory, Ticket

def populate():
    # Tickets already cleared manually via sqlite3

    print("Clearing existing categories...")
    Category.objects.all().delete()
    print("Categories cleared.")

    categories_data = {
        "Computer & Laptop Support": [
            "PC & Laptop Troubleshooting",
            "Windows Installation & Activation",
            "macOS Support",
            "Linux Installation & Support",
            "Driver Installation",
            "Software Installation & Configuration",
            "Virus & Malware Removal",
            "Performance Optimization",
            "Data Backup & Recovery",
            "Hardware Diagnostics",
            "SSD/RAM Upgrade Support",
            "Printer & Scanner Setup"
        ],
        "Network & Internet Support": [
            "Wi-Fi Setup & Optimization",
            "Router Configuration",
            "Internet Troubleshooting",
            "LAN/WAN Configuration",
            "Network Security",
            "Mesh Wi-Fi Installation",
            "Office Network Setup"
        ],
        "Smart Home & On-Site Support": [
            "Smart TV Setup",
            "Smart Home Device Installation",
            "CCTV Installation & Configuration",
            "IP Camera Setup",
            "Door Access System",
            "Home Office Setup"
        ],
        "Cloud & Business IT Services": [
            "Microsoft 365 Setup",
            "Google Workspace Setup",
            "Email Configuration",
            "Cloud Storage Setup",
            "Server Configuration",
            "NAS Setup",
            "Backup Solutions"
        ],
        "Cyber Security": [
            "Security Checkup",
            "Virus Protection",
            "Firewall Configuration",
            "Password Management",
            "Data Privacy Consultation"
        ],
        "Mobile Support": [
            "Android Troubleshooting",
            "iPhone Support",
            "Mobile Data Backup",
            "Phone Setup",
            "App Installation",
            "Device Optimization"
        ],
        "Business IT Support": [
            "IT Consultancy",
            "Annual Maintenance Contract (AMC)",
            "Remote Monitoring",
            "Office IT Support",
            "POS System Setup",
            "IT Asset Management"
        ],
        "Remote Support": [
            "Remote Desktop Support",
            "Live Chat Assistance",
            "Video Call Support",
            "Screen Sharing Support",
            "Emergency IT Assistance"
        ]
    }

    print("Populating new categories...")
    for cat_name, subcats in categories_data.items():
        category = Category.objects.create(name=cat_name)
        for subcat_name in subcats:
            SubCategory.objects.create(category=category, name=subcat_name)
    
    print("Categories populated successfully!")

if __name__ == '__main__':
    populate()
