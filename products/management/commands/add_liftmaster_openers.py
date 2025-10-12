# products/management/commands/add_liftmaster_openers.py
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from products.models import Product, ProductCategory, OpenerSpecifications
import requests
import time


class Command(BaseCommand):
    help = 'Add all LiftMaster Middle East garage door opener products (20+ products)'

    def download_image(self, url, product_name):
        """Download image from URL with better error handling"""
        try:
            if not url:
                return None
                
            # Add https:// if missing
            if url.startswith('//'):
                url = 'https:' + url
            elif not url.startswith('http'):
                url = 'https://www.liftmaster-me.com' + url
            
            self.stdout.write(f'    📥 Downloading: {url[:80]}...')
            
            # Better headers to avoid 403
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.liftmaster-me.com/products/',
                'Sec-Fetch-Dest': 'image',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site',
            }
            
            response = requests.get(url, timeout=20, headers=headers, allow_redirects=True)
            response.raise_for_status()
            
            # Check if we got actual image data
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type and len(response.content) < 1000:
                raise Exception(f"Not a valid image")
            
            # Determine extension
            if 'webp' in content_type:
                ext = 'webp'
            elif 'png' in content_type:
                ext = 'png'
            elif 'jpeg' in content_type or 'jpg' in content_type:
                ext = 'jpg'
            else:
                ext = 'jpg'
            
            filename = f"{product_name.lower().replace(' ', '_').replace('-', '_')[:50]}.{ext}"
            self.stdout.write(self.style.SUCCESS(f'    ✅ Image downloaded'))
            return ContentFile(response.content, name=filename)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'    ⚠️ Could not download image: {str(e)[:60]}'))
            return None

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('  Adding LiftMaster Middle East Products'))
        self.stdout.write(self.style.SUCCESS('  Source: https://www.liftmaster-me.com/products/'))
        self.stdout.write(self.style.SUCCESS('='*70))
        
        # Create opener category
        openers_category, _ = ProductCategory.objects.get_or_create(
            slug='garage-door-openers',
            defaults={
                'name': 'Garage Door Openers',
                'name_en': 'Garage Door Openers',
                'description': 'Professional garage door openers from LiftMaster Middle East',
                'icon': 'fa-tools',
                'order': 2,
                'is_active': True
            }
        )
        
        # All LiftMaster ME products from their website
        opener_products = [
            # ========== SECTIONAL GARAGE DOOR OPENERS ==========
            {
                'name': 'LiftMaster LM-W8ME Wall Mount',
                'name_en': 'LiftMaster LM-W8ME Wall Mount',
                'model_number': 'LM-W8ME',
                'brand': 'LiftMaster',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2022/03/MESDO.PNG.png',
                'short_description': 'Premium Wall-Mount Sectional Door Opener - Space-Saving Design',
                'description': '''The LiftMaster LM-W8ME is an innovative wall-mount garage door opener designed specifically for sectional garage doors. This space-saving solution eliminates the need for overhead tracks and mounting hardware, freeing up valuable ceiling space for storage.

Perfect for garages with limited headroom, high ceilings, or where you simply want to maximize your garage space. The wall-mount design provides a clean, modern look while delivering reliable, powerful performance.

Features LiftMaster's advanced technology with smooth, quiet operation and comprehensive safety features including auto-stop and reverse functionality.''',
                'features': '''✓ Wall-Mount Design - Saves Ceiling Space
✓ For Sectional Garage Doors
✓ Powerful & Reliable Motor
✓ Quiet Operation
✓ Auto-Stop & Reverse Safety
✓ Weather Resistant Construction
✓ Professional Installation
✓ Ideal for Low Headroom
✓ Space-Saving Solution
✓ Modern Clean Look''',
                'specifications': '''Model: LM-W8ME
Type: Wall-Mount Sectional Door Opener
Application: Residential & Light Commercial
Power: AC Motor
Mounting: Side Wall Installation
Operation: Ultra-Quiet
Safety: Auto-Stop & Reverse
Finish: Weather-Resistant
Warranty: LiftMaster Warranty''',
                'drive_type': 'jackshaft',
                'horsepower': '0.75',
                'has_wifi': False,
                'has_battery_backup': False,
                'has_smart_features': False,
                'is_featured': True,
                'order': 1,
            },
            {
                'name': 'LiftMaster LM3800TXSA',
                'name_en': 'LiftMaster LM3800TXSA',
                'model_number': 'LM3800TXSA',
                'brand': 'LiftMaster',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2021/02/eyJ3IjoyMDQ4LCJoIjoyMDQ4LCJzY29wZSI6ImFwcCJ9-3-1152x1536-1.webp',
                'short_description': 'Heavy-Duty Sectional Door Opener with Weather Protection',
                'description': '''The LiftMaster LM3800TXSA is engineered for demanding applications requiring weather-resistant performance. This robust sectional door opener is built to withstand harsh environmental conditions while maintaining reliable operation.

Ideal for coastal areas or regions with extreme weather, the LM3800TXSA features enhanced weather protection and corrosion-resistant components. The heavy-duty motor provides powerful lifting capacity for large sectional doors.

Perfect for both residential and commercial applications where durability and reliability are essential.''',
                'features': '''✓ Weather-Resistant Design
✓ Heavy-Duty Construction
✓ Corrosion-Resistant Components
✓ Powerful Motor
✓ For Large Sectional Doors
✓ Reliable Performance
✓ Commercial Grade
✓ Enhanced Durability
✓ All-Weather Operation
✓ Professional Quality''',
                'specifications': '''Model: LM3800TXSA
Type: Heavy-Duty Sectional Opener
Application: Residential & Commercial
Weather Rating: Weather-Resistant
Power: Heavy-Duty AC Motor
Capacity: Large Doors
Protection: Corrosion-Resistant
Operation: Reliable & Smooth
Warranty: Extended Warranty Available''',
                'drive_type': 'chain',
                'horsepower': '1.00',
                'has_wifi': False,
                'has_battery_backup': False,
                'has_smart_features': False,
                'is_featured': True,
                'order': 2,
            },
            {
                'name': 'LiftMaster LM80EV DC Motor',
                'name_en': 'LiftMaster LM80EV DC Motor',
                'model_number': 'LM80EV',
                'brand': 'LiftMaster',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2021/02/LM80_LM100_LM120-e1619682465629.webp',
                'short_description': 'Energy-Efficient DC Motor Sectional Door Opener',
                'description': '''The LiftMaster LM80EV features an advanced DC motor technology that delivers exceptional energy efficiency without compromising performance. This modern opener is designed for environmentally conscious homeowners who want to reduce energy consumption.

The DC motor provides ultra-quiet operation, making it perfect for homes with living spaces adjacent to or above the garage. Enhanced with EV (Electronic Variable) speed control for smooth starts and stops.

Features soft start and soft stop technology to minimize wear on your door and opener, extending the life of your system.''',
                'features': '''✓ DC Motor Technology
✓ Energy Efficient
✓ Ultra-Quiet Operation
✓ Soft Start & Stop
✓ Electronic Variable Speed
✓ Smooth Performance
✓ Reduced Energy Consumption
✓ Perfect for Attached Garages
✓ Extended Lifespan
✓ Modern Technology''',
                'specifications': '''Model: LM80EV
Motor Type: DC Motor
Technology: Electronic Variable Speed
Power Consumption: Energy Efficient
Application: Residential Sectional Doors
Operation: Ultra-Quiet
Features: Soft Start/Stop
Mounting: Ceiling Mount
Warranty: Standard LiftMaster''',
                'drive_type': 'belt',
                'horsepower': '0.50',
                'has_wifi': False,
                'has_battery_backup': False,
                'has_smart_features': True,
                'is_featured': True,
                'order': 3,
            },
            {
                'name': 'LiftMaster LM100EV',
                'name_en': 'LiftMaster LM100EV',
                'model_number': 'LM100EV',
                'brand': 'LiftMaster',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2021/02/LM80_LM100_LM120-2.jpeg',
                'short_description': 'Mid-Range DC Motor Opener with Enhanced Features',
                'description': '''The LiftMaster LM100EV represents the perfect balance of performance and value. This mid-range DC motor opener offers enhanced features and capabilities for standard to larger sectional garage doors.

Building on the success of the LM80EV, the LM100EV adds increased power and advanced control features. The DC motor technology ensures whisper-quiet operation while maintaining strong lifting performance.

Ideal for families who want reliable, quiet operation with modern features at a competitive price point.''',
                'features': '''✓ Enhanced DC Motor
✓ Increased Power Output
✓ Whisper-Quiet Operation
✓ Advanced Controls
✓ Soft Start/Stop Technology
✓ Energy Saving
✓ Smooth Performance
✓ Reliable Operation
✓ Modern Design
✓ Great Value''',
                'specifications': '''Model: LM100EV
Motor: Enhanced DC Motor
Power: Mid-Range Performance
Application: Standard to Large Doors
Technology: Electronic Variable
Operation: Whisper-Quiet
Control: Advanced Digital
Efficiency: High Energy Rating
Warranty: LiftMaster Standard''',
                'drive_type': 'belt',
                'horsepower': '0.75',
                'has_wifi': False,
                'has_battery_backup': False,
                'has_smart_features': True,
                'is_featured': False,
                'order': 4,
            },
            {
                'name': 'LiftMaster LM130EV Premium',
                'name_en': 'LiftMaster LM130EV Premium',
                'model_number': 'LM130EV',
                'brand': 'LiftMaster',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2021/02/LM80_LM100_LM120-e1619682465629.webp',
                'short_description': 'Premium DC Motor Opener - Top of the Line Performance',
                'description': '''The LiftMaster LM130EV is the flagship of the EV series, offering premium performance and the most advanced features. This top-tier DC motor opener is designed for those who demand the very best in garage door operation.

Featuring maximum power, ultra-smooth operation, and comprehensive safety features, the LM130EV handles even the heaviest sectional doors with ease. The premium DC motor operates at whisper-quiet levels while delivering exceptional lifting power.

Perfect for luxury homes, custom installations, or any application where performance and quality are paramount.''',
                'features': '''✓ Premium DC Motor - Maximum Power
✓ Ultra-Smooth Operation
✓ Whisper-Quiet Performance
✓ Handles Heavy Doors
✓ Advanced Safety Features
✓ Soft Start/Stop Premium
✓ Energy Efficient
✓ Superior Build Quality
✓ Top-Tier Performance
✓ Luxury Features''',
                'specifications': '''Model: LM130EV
Class: Premium/Flagship
Motor: High-Performance DC
Power: Maximum Output
Application: Heavy/Large Doors
Technology: Advanced EV Control
Operation: Ultra-Whisper-Quiet
Features: Full Safety Suite
Quality: Professional Grade
Warranty: Extended Available''',
                'drive_type': 'belt',
                'horsepower': '1.00',
                'has_wifi': False,
                'has_battery_backup': False,
                'has_smart_features': True,
                'is_featured': True,
                'order': 5,
            },
            {
                'name': 'LiftMaster 5580-2GBSA (Discontinued)',
                'name_en': 'LiftMaster 5580-2GBSA',
                'model_number': '5580-2GBSA',
                'brand': 'LiftMaster',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2021/02/Chamberlain-Product-4.webp',
                'short_description': 'Legacy Model - Replacement Parts Available',
                'description': '''The LiftMaster 5580-2GBSA is a discontinued model that served many customers reliably over the years. While no longer in production, replacement parts and service support remain available for existing installations.

If you have this model and need service or repairs, LiftMaster continues to support legacy products with genuine parts and technical assistance. For new installations, we recommend upgrading to current models like the LM80EV, LM100EV, or LM130EV series.

Contact us for information about compatible replacement models or service options for your existing 5580-2GBSA opener.''',
                'features': '''✓ Legacy Model
✓ Parts Still Available
✓ Service Support Continues
✓ Proven Reliability
✓ Sectional Door Compatible
✓ Upgrade Options Available
✓ Trade-In Programs
✓ Technical Support
✓ Replacement Recommended
✓ Contact for Service''',
                'specifications': '''Model: 5580-2GBSA
Status: Discontinued
Parts: Available
Service: Supported
Replacement: Current EV Series
Upgrade Path: LM80/100/130EV
Support: Technical Available
Warranty: Legacy Support''',
                'drive_type': 'chain',
                'horsepower': '0.50',
                'has_wifi': False,
                'has_battery_backup': False,
                'has_smart_features': False,
                'is_featured': False,
                'order': 20,
            },
            
            # ========== ROLLER GARAGE DOOR OPENERS ==========
            {
                'name': 'LiftMaster LM555EVGBSA Weather Resistant',
                'name_en': 'LiftMaster LM555EVGBSA Weather Resistant',
                'model_number': 'LM555EVGBSA',
                'brand': 'LiftMaster',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2021/11/LM555EVGBSA-resize.webp',
                'short_description': 'Heavy-Duty Weather-Resistant Roller Door Opener',
                'description': '''The LiftMaster LM555EVGBSA is specifically engineered for roller garage doors in harsh weather conditions. This weather-resistant opener is built to withstand coastal environments, high humidity, and extreme temperatures.

Features advanced corrosion protection and sealed components to ensure reliable operation year-round. The robust motor provides powerful lifting for roller doors while maintaining smooth, quiet operation.

Perfect for homes in coastal areas, humid climates, or regions with challenging weather conditions. The GBSA rating indicates superior weather protection and durability.''',
                'features': '''✓ Weather-Resistant Design
✓ Corrosion Protection
✓ For Roller Doors
✓ Sealed Components
✓ Heavy-Duty Motor
✓ Coastal Environment Rated
✓ All-Weather Performance
✓ Humidity Resistant
✓ Temperature Tolerant
✓ GBSA Certified''',
                'specifications': '''Model: LM555EVGBSA
Type: Weather-Resistant Roller Opener
Application: Roller Garage Doors
Weather Rating: GBSA Certified
Protection: Corrosion-Resistant
Environment: Coastal/Humid
Motor: Heavy-Duty AC
Operation: Smooth & Quiet
Warranty: Extended Weather Protection''',
                'drive_type': 'direct',
                'horsepower': '0.75',
                'has_wifi': False,
                'has_battery_backup': False,
                'has_smart_features': False,
                'is_featured': True,
                'order': 6,
            },
            {
                'name': 'LiftMaster LM955GBME Commercial Roller',
                'name_en': 'LiftMaster LM955GBME Commercial Roller',
                'model_number': 'LM955GBME',
                'brand': 'LiftMaster',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2025/04/LM955GBME-Hero-FL.png',
                'short_description': 'Light Commercial Roller Door Opener - Professional Grade',
                'description': '''The LiftMaster LM955GBME is a light commercial roller door opener designed for business and industrial applications. This professional-grade opener delivers the power and reliability needed for frequent daily use.

Built for commercial environments, the LM955GBME features an industrial-strength motor, heavy-duty components, and enhanced safety features required for commercial installations. Perfect for retail stores, warehouses, workshops, and commercial garages.

Meets commercial building codes and safety standards while providing years of reliable, maintenance-free operation.''',
                'features': '''✓ Light Commercial Grade
✓ Industrial-Strength Motor
✓ Heavy-Duty Construction
✓ High Cycle Rating
✓ For Frequent Use
✓ Commercial Safety Features
✓ Reliable Performance
✓ Professional Installation
✓ Code Compliant
✓ Low Maintenance''',
                'specifications': '''Model: LM955GBME
Class: Light Commercial
Application: Roller Doors (Commercial)
Use: Retail/Warehouse/Workshop
Motor: Industrial-Strength
Duty Cycle: High Frequency
Safety: Commercial Standards
Installation: Professional Required
Warranty: Commercial Warranty''',
                'drive_type': 'direct',
                'horsepower': '1.00',
                'has_wifi': False,
                'has_battery_backup': False,
                'has_smart_features': False,
                'is_featured': True,
                'order': 7,
            },
            {
                'name': 'LiftMaster LM550EVGBSA (Discontinued)',
                'name_en': 'LiftMaster LM550EVGBSA',
                'model_number': 'LM550EVGBSA',
                'brand': 'LiftMaster',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2021/02/eyJ3IjoyMDQ4LCJoIjoyMDQ4LCJzY29wZSI6ImFwcCJ9-2-1024x1536-1.webp',
                'short_description': 'Legacy Roller Door Model - Service Available',
                'description': '''The LiftMaster LM550EVGBSA is a discontinued roller door opener model. While no longer in production, parts and service remain available for existing installations.

This model served as a reliable solution for roller garage doors and continues to be supported with genuine LiftMaster parts. For new installations, we recommend the current LM555EVGBSA model which offers improved features and updated technology.

Contact us for upgrade options or service information for your existing LM550EVGBSA opener.''',
                'features': '''✓ Legacy Roller Door Model
✓ Parts Available
✓ Service Supported
✓ Upgrade Path: LM555EVGBSA
✓ Roller Door Compatible
✓ Technical Support
✓ Replacement Options
✓ Trade-In Available
✓ Contact for Service''',
                'specifications': '''Model: LM550EVGBSA
Status: Discontinued
Type: Roller Door Opener
Parts: Available
Service: Supported
Replacement: LM555EVGBSA
Support: Technical Assistance
Warranty: Legacy Support''',
                'drive_type': 'direct',
                'horsepower': '0.50',
                'has_wifi': False,
                'has_battery_backup': False,
                'has_smart_features': False,
                'is_featured': False,
                'order': 21,
            },
            
            # ========== INDUSTRIAL & COMMERCIAL OPERATORS ==========
            {
                'name': 'Grifco Manual Hoist Roller Door',
                'name_en': 'Grifco Manual Hoist Roller Door',
                'model_number': 'GRIFCO-HOIST',
                'brand': 'Grifco',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2021/02/manual-hoists-1024x580-1.png',
                'short_description': 'Manual Hoist System for Roller Doors - No Power Required',
                'description': '''The Grifco Manual Hoist is a reliable manual operation system for roller doors where electric power is unavailable or not preferred. This mechanical hoist provides smooth, controlled operation without electricity.

Perfect for remote locations, backup systems, or applications where simplicity and reliability are priorities. The manual hoist features gear reduction for easy operation even with heavy roller doors.

Ideal for agricultural buildings, storage facilities, or any location where a simple, dependable solution is needed.''',
                'features': '''✓ Manual Operation
✓ No Electricity Required
✓ Mechanical Hoist System
✓ Gear Reduction
✓ Easy to Operate
✓ For Heavy Doors
✓ Reliable & Simple
✓ Low Maintenance
✓ Perfect for Remote Areas
✓ Backup Solution''',
                'specifications': '''Model: Manual Hoist
Brand: Grifco
Power: Manual Operation
Type: Mechanical Hoist
Application: Roller Doors
Operation: Hand-Operated
Features: Gear Reduction
Maintenance: Minimal
Installation: Simple
Warranty: Mechanical Warranty''',
                'drive_type': 'other',
                'horsepower': '0.00',
                'has_wifi': False,
                'has_battery_backup': False,
                'has_smart_features': False,
                'is_featured': False,
                'order': 8,
            },
            {
                'name': 'GH Elite Commercial Door Operator',
                'name_en': 'GH Elite Commercial Door Operator',
                'model_number': 'GH-ELITE',
                'brand': 'LiftMaster',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2021/02/admin-ajax-1.png',
                'short_description': 'Elite Commercial Operator for Roller Shutters',
                'description': '''The GH Elite is a premium commercial door operator designed for demanding commercial and industrial applications. This elite-class operator delivers superior performance, durability, and reliability for high-traffic installations.

Features industrial-grade components, advanced control systems, and comprehensive safety features required for commercial environments. Built to handle intensive daily use with minimal maintenance.

Perfect for commercial buildings, industrial facilities, and any application requiring professional-grade performance and reliability.''',
                'features': '''✓ Elite Commercial Grade
✓ Industrial Components
✓ High-Traffic Rated
✓ Advanced Controls
✓ Heavy-Duty Performance
✓ Comprehensive Safety
✓ Minimal Maintenance
✓ Professional Installation
✓ Code Compliant
✓ Extended Warranty''',
                'specifications': '''Model: GH Elite
Class: Commercial Elite
Application: Roller Shutters/Commercial
Environment: Industrial/Commercial
Duty: Heavy/High-Traffic
Control: Advanced Digital
Safety: Full Commercial Suite
Installation: Professional
Warranty: Extended Commercial''',
                'drive_type': 'direct',
                'horsepower': '1.50',
                'has_wifi': False,
                'has_battery_backup': False,
                'has_smart_features': True,
                'is_featured': True,
                'order': 9,
            },
            {
                'name': 'Fire Door Operator',
                'name_en': 'Fire Door Operator',
                'model_number': 'FIRE-DOOR-OP',
                'brand': 'LiftMaster',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2021/02/Chamberlain-Group_Product-152-transparent-2.jpeg',
                'short_description': 'Certified Fire-Rated Door Operator with Safety Features',
                'description': '''The LiftMaster Fire Door Operator is specifically engineered and certified for fire-rated door applications. This specialized operator meets strict fire safety codes and includes automatic closing features required by building regulations.

Features fire-rated components, smoke detector integration, and emergency operation modes. The operator automatically closes fire doors upon alarm activation, helping to contain fire and smoke.

Essential for commercial buildings, apartments, and any facility requiring fire-rated door systems.''',
                'features': '''✓ Fire-Rated Certified
✓ Code Compliant
✓ Smoke Detector Integration
✓ Emergency Close Function
✓ Automatic Operation
✓ Safety Certified
✓ Fire-Rated Components
✓ Building Code Approved
✓ Professional Grade
✓ Life Safety System''',
                'specifications': '''Model: Fire Door Operator
Certification: Fire-Rated
Application: Fire Doors/Safety
Integration: Smoke Detectors
Operation: Emergency Auto-Close
Compliance: Building Codes
Safety: Life Safety Certified
Installation: Professional Required
Warranty: Fire Safety Warranty''',
                'drive_type': 'direct',
                'horsepower': '1.00',
                'has_wifi': False,
                'has_battery_backup': True,
                'has_smart_features': True,
                'is_featured': True,
                'order': 10,
            },
            {
                'name': 'HD75 Industrial Door Opener',
                'name_en': 'HD75 Industrial Door Opener',
                'model_number': 'HD75',
                'brand': 'LiftMaster',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2021/02/Chamberlain-Group_Product-131-transparent-5.jpg',
                'short_description': 'Heavy-Duty Industrial Opener for Large Doors & Grilles',
                'description': '''The HD75 is LiftMaster's heavy-duty industrial door opener designed for the most demanding applications. This powerful operator handles large industrial doors, roller shutters, and security grilles with ease.

Built with industrial-grade components and an extra-heavy-duty motor, the HD75 is engineered for continuous operation in harsh industrial environments. Perfect for warehouses, factories, distribution centers, and heavy industrial facilities.

Features advanced control systems, comprehensive safety features, and the durability to withstand years of intensive use.''',
                'features': '''✓ Heavy-Duty Industrial
✓ Extra-Powerful Motor
✓ For Large Doors/Grilles
✓ Continuous Operation Rated
✓ Industrial Environment
✓ Advanced Controls
✓ Heavy-Duty Components
✓ High Cycle Rating
✓ Professional Grade
✓ Extended Life''',
                'specifications': '''Model: HD75
Class: Heavy-Duty Industrial
Application: Large Doors/Grilles
Environment: Industrial/Harsh
Motor: Extra Heavy-Duty
Cycle Rating: Continuous
Control: Industrial Digital
Capacity: Extra Large Doors
Installation: Industrial
Warranty: Heavy-Duty Industrial''',
                'drive_type': 'direct',
                'horsepower': '2.00',
                'has_wifi': False,
                'has_battery_backup': False,
                'has_smart_features': True,
                'is_featured': True,
                'order': 11,
            },
            {
                'name': 'E-Drive MK6 Roller Shutter',
                'name_en': 'E-Drive MK6 Roller Shutter',
                'model_number': 'E-DRIVE-MK6',
                'brand': 'Grifco',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2021/02/Chamberlain-Group_Product-111-transparent-2.jpeg',
                'short_description': 'Latest Generation Electronic Roller Shutter Operator',
                'description': '''The E-Drive MK6 represents the latest generation in electronic roller shutter technology. This advanced operator features modern electronic controls, improved efficiency, and enhanced features over previous models.

Building on the proven E-Drive platform, the MK6 adds updated electronics, quieter operation, and improved reliability. Perfect for residential, commercial, and light industrial roller shutters.

Features electronic limit switches, obstacle detection, and energy-efficient operation.''',
                'features': '''✓ Latest MK6 Generation
✓ Electronic Controls
✓ Improved Efficiency
✓ Quieter Operation
✓ Electronic Limit Switches
✓ Obstacle Detection
✓ Energy Efficient
✓ Modern Design
✓ Reliable Performance
✓ Easy Installation''',
                'specifications': '''Model: E-Drive MK6
Generation: Latest (MK6)
Type: Electronic Roller Operator
Application: Roller Shutters
Control: Electronic Digital
Features: Obstacle Detection
Operation: Quiet & Smooth
Efficiency: Energy Optimized
Installation: Standard
Warranty: Standard Grifco''',
                'drive_type': 'direct',
                'horsepower': '0.50',
                'has_wifi': False,
                'has_battery_backup': False,
                'has_smart_features': True,
                'is_featured': False,
                'order': 12,
            },
            {
                'name': 'E-Drive MK5 (Discontinued)',
                'name_en': 'E-Drive MK5',
                'model_number': 'E-DRIVE-MK5',
                'brand': 'Grifco',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2021/02/Chamberlain-Group_Product-111-transparent-2.jpeg',
                'short_description': 'Previous Generation - Upgrade to MK6 Available',
                'description': '''The E-Drive MK5 is the previous generation roller shutter operator. While discontinued, parts and service remain available for existing installations.

The MK5 served reliably for many years and continues to be supported with genuine parts. For new installations or upgrades, we recommend the current E-Drive MK6 model which offers improved features and updated technology.

Contact us for upgrade options or service information for your existing E-Drive MK5 operator.''',
                'features': '''✓ Previous Generation MK5
✓ Parts Available
✓ Service Supported
✓ Upgrade to MK6 Available
✓ Proven Reliability
✓ Technical Support
✓ Replacement Options
✓ Trade-In Programs
✓ Contact for Service''',
                'specifications': '''Model: E-Drive MK5
Status: Discontinued
Type: Electronic Roller Operator
Parts: Available
Service: Supported
Replacement: E-Drive MK6
Support: Technical Available
Warranty: Legacy Support''',
                'drive_type': 'direct',
                'horsepower': '0.50',
                'has_wifi': False,
                'has_battery_backup': False,
                'has_smart_features': False,
                'is_featured': False,
                'order': 22,
            },
            
            # ========== ACCESSORIES ==========
            {
                'name': '041A4166 Lighted Push Button',
                'name_en': '041A4166 Lighted Push Button Control',
                'model_number': '041A4166',
                'brand': 'LiftMaster',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2022/11/041A4166.png',
                'short_description': 'Illuminated Wall-Mounted Push Button Control',
                'description': '''The 041A4166 is a professional-grade lighted push button control designed for LiftMaster garage door openers. This illuminated control provides clear visibility day or night and adds convenient wall-mounted operation.

Features a durable design with illuminated button for easy location in dark garages. Simple push-button operation makes it ideal for all users, and the lighted indicator shows power status at a glance.

Easy to install and compatible with most LiftMaster residential and commercial openers.''',
                'features': '''✓ Illuminated Button
✓ Wall-Mounted
✓ Easy to Locate
✓ Clear Visibility
✓ Power Indicator Light
✓ Durable Construction
✓ Simple Operation
✓ Easy Installation
✓ Universal Compatible
✓ Professional Grade''',
                'specifications': '''Model: 041A4166
Type: Lighted Push Button Control
Mounting: Wall-Mount
Illumination: LED Backlit
Compatibility: LiftMaster Openers
Installation: Simple 2-Wire
Power: Low Voltage
Durability: Professional Grade
Warranty: Accessory Warranty''',
                'drive_type': 'other',
                'horsepower': '0.00',
                'has_wifi': False,
                'has_battery_backup': False,
                'has_smart_features': False,
                'is_featured': False,
                'order': 13,
            },
            {
                'name': '128EV Wireless Wall Control',
                'name_en': '128EV Wireless Wall Control',
                'model_number': '128EV',
                'brand': 'LiftMaster',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2022/12/128ev.png',
                'short_description': 'Advanced Wireless Wall-Mounted Control Panel',
                'description': '''The 128EV Wireless Wall Control brings modern convenience to your garage with advanced features and wireless installation. This sophisticated control panel eliminates the need for wiring while providing comprehensive control of your LiftMaster opener.

Features wireless communication, timer-to-close functionality, and vacation lock for added security. The large LCD display shows door status and system information at a glance.

Battery-powered for easy installation anywhere in your garage, and includes motion-activated lighting for nighttime convenience.''',
                'features': '''✓ Wireless Installation
✓ No Wiring Required
✓ Large LCD Display
✓ Timer-to-Close Function
✓ Vacation Lock Mode
✓ Motion-Activated Light
✓ Battery Powered
✓ Door Status Display
✓ Modern Design
✓ Easy to Install''',
                'specifications': '''Model: 128EV
Type: Wireless Wall Control
Communication: Wireless RF
Display: LCD Screen
Power: Battery Operated
Features: Timer-to-Close, Vacation Lock
Lighting: Motion-Activated
Compatibility: LiftMaster EV Series
Range: Interior Garage
Warranty: Electronic Warranty''',
                'drive_type': 'other',
                'horsepower': '0.00',
                'has_wifi': False,
                'has_battery_backup': True,
                'has_smart_features': True,
                'is_featured': True,
                'order': 14,
            },
            {
                'name': '828EV MyQ Internet Gateway',
                'name_en': '828EV MyQ Internet Gateway',
                'model_number': '828EV',
                'brand': 'LiftMaster',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2022/12/828ev.png',
                'short_description': 'Smart Home Integration - Control from Anywhere',
                'description': '''The 828EV MyQ Internet Gateway transforms your existing LiftMaster opener into a smart, connected system. This revolutionary device enables smartphone control and monitoring from anywhere in the world.

Connect your garage door opener to your home WiFi network and gain complete control through the MyQ smartphone app. Receive alerts when your door opens or closes, grant access to visitors, and integrate with smart home systems.

Works with Amazon Alexa, Google Assistant, and other smart home platforms for voice control and automation.''',
                'features': '''✓ MyQ Smart Technology
✓ WiFi Connected
✓ Smartphone Control
✓ Remote Access - Anywhere
✓ Real-Time Alerts
✓ Amazon Alexa Compatible
✓ Google Assistant Compatible
✓ Guest Access Control
✓ Activity History
✓ Smart Home Integration''',
                'specifications': '''Model: 828EV
Type: Internet Gateway
Technology: MyQ Smart Hub
Connectivity: WiFi
Control: Smartphone App (iOS/Android)
Integration: Alexa, Google, IFTTT
Features: Alerts, Remote Access
Compatibility: LiftMaster EV Openers
Installation: Plug & Play
Warranty: Electronic Warranty''',
                'drive_type': 'other',
                'horsepower': '0.00',
                'has_wifi': True,
                'has_battery_backup': False,
                'has_smart_features': True,
                'is_featured': True,
                'order': 15,
            },
            {
                'name': 'C10A-4 Grifco Standard Control',
                'name_en': 'C10A-4 Grifco Standard E-Drive Control',
                'model_number': 'C10A-4',
                'brand': 'Grifco',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2022/12/c10a-4.png',
                'short_description': 'Standard Control Panel for E-Drive Operators',
                'description': '''The C10A-4 is the standard control panel designed specifically for Grifco E-Drive roller shutter operators. This reliable control unit provides essential operation and safety features for residential and light commercial applications.

Features electronic controls, safety inputs, and standard programming for E-Drive systems. The control panel includes obstacle detection, limit switch settings, and force adjustment.

Simple to install and program, making it ideal for residential installations and light commercial use.''',
                'features': '''✓ Standard E-Drive Control
✓ Electronic Controls
✓ Obstacle Detection
✓ Limit Switch Settings
✓ Force Adjustment
✓ Safety Inputs
✓ Easy Programming
✓ Reliable Operation
✓ Residential/Light Commercial
✓ Grifco Compatible''',
                'specifications': '''Model: C10A-4
Type: Electronic Control Panel
Application: E-Drive Operators
Features: Safety, Limits, Force
Programming: Simple Digital
Compatibility: Grifco E-Drive
Environment: Indoor/Protected
Installation: Standard
Warranty: Electronic Warranty''',
                'drive_type': 'other',
                'horsepower': '0.00',
                'has_wifi': False,
                'has_battery_backup': False,
                'has_smart_features': False,
                'is_featured': False,
                'order': 16,
            },
            {
                'name': 'G890MAX 3-Button Remote',
                'name_en': 'G890MAX 3-Button Mini Remote Control',
                'model_number': 'G890MAX',
                'brand': 'LiftMaster',
                'image_url': 'https://www.liftmaster-me.com/wp-content/uploads/2022/12/890MAX.png',
                'short_description': 'Compact 3-Button Remote - Controls Up to 3 Doors',
                'description': '''The G890MAX is a versatile 3-button mini remote control that can operate up to three LiftMaster garage door openers or gates. This compact remote fits easily on your keychain or visor clip.

Features Security+ 2.0 rolling code technology for enhanced security and compatibility with most LiftMaster residential openers. The three-button design allows you to control multiple doors or share access among family members.

Durable construction with weather-resistant design for reliable operation in all conditions. Battery-powered with long life and easy battery replacement.''',
                'features': '''✓ 3-Button Design
✓ Controls 3 Doors/Gates
✓ Compact Mini Size
✓ Security+ 2.0 Technology
✓ Rolling Code Encryption
✓ Keychain Compatible
✓ Visor Clip Included
✓ Weather-Resistant
✓ Long Battery Life
✓ Easy Programming''',
                'specifications': '''Model: G890MAX
Type: 3-Button Mini Remote
Buttons: 3 (Up to 3 Doors)
Security: Security+ 2.0
Technology: Rolling Code
Range: Standard Residential
Battery: Replaceable Coin Cell
Size: Compact/Mini
Compatibility: LiftMaster Openers
Warranty: Remote Warranty''',
                'drive_type': 'other',
                'horsepower': '0.00',
                'has_wifi': False,
                'has_battery_backup': False,
                'has_smart_features': False,
                'is_featured': False,
                'order': 17,
            },
        ]
        
        # Add products
        added_count = 0
        skipped_count = 0
        
        for idx, product_data in enumerate(opener_products, 1):
            self.stdout.write(f'\n📦 Processing {idx}/{len(opener_products)}: {product_data["name"]}')
            
            # Extract opener specs data
            drive_type = product_data.pop('drive_type')
            horsepower = product_data.pop('horsepower')
            has_wifi = product_data.pop('has_wifi')
            has_battery_backup = product_data.pop('has_battery_backup')
            has_smart_features = product_data.pop('has_smart_features')
            image_url = product_data.pop('image_url', None)
            
            # Create product
            product, created = Product.objects.get_or_create(
                slug=product_data['name_en'].lower().replace(' ', '-').replace('--', '-'),
                defaults={
                    **product_data,
                    'category': openers_category,
                    'product_type': 'opener',
                    'is_active': True,
                }
            )
            
            if created:
                added_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✅ Added: {product.name_en}'))
                
                # Download image
                if image_url and not product.image:
                    image_file = self.download_image(image_url, product.name_en)
                    if image_file:
                        product.image.save(image_file.name, image_file, save=True)
                    time.sleep(0.5)  # Be nice to servers
                
                # Create opener specifications
                opener_spec, spec_created = OpenerSpecifications.objects.get_or_create(
                    product=product,
                    defaults={
                        'drive_type': drive_type,
                        'horsepower': horsepower,
                        'has_wifi': has_wifi,
                        'has_battery_backup': has_battery_backup,
                        'has_smart_features': has_smart_features,
                        'has_camera': False,
                        'lifting_capacity': 'Standard' if float(horsepower) < 1.0 else 'Heavy-Duty',
                        'speed': 'Standard',
                        'noise_level': 'Quiet' if drive_type in ['belt', 'jackshaft'] else 'Standard',
                        'warranty_years': 10 if 'Elite' in product.name or 'Premium' in product.name else 5,
                    }
                )
                
                if spec_created:
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Added specifications'))
            else:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f'  ⏭️  Already exists: {product.name_en}'))
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('  ✅ All LiftMaster Middle East products processed!'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS(f'  📊 Total products: {len(opener_products)}'))
        self.stdout.write(self.style.SUCCESS(f'  ✅ Added: {added_count}'))
        self.stdout.write(self.style.SUCCESS(f'  ⏭️  Skipped (already exist): {skipped_count}'))
        self.stdout.write(self.style.SUCCESS(f'  🔍 View at: /admin/products/product/'))
        self.stdout.write(self.style.SUCCESS('='*70))
