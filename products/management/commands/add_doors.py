# products/management/commands/add_doors.py
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from products.models import Product, ProductCategory, DoorSpecifications
import requests
from io import BytesIO
import time


class Command(BaseCommand):
    help = 'Add garage door products from Protech website to database'
    
    def download_image(self, url, product_name):
        """Download image from URL and return ContentFile"""
        try:
            self.stdout.write(f'    Downloading image from: {url}')
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Get image extension from URL or content type
            content_type = response.headers.get('content-type', '')
            if 'image/jpeg' in content_type or url.endswith('.jpg') or url.endswith('.jpeg'):
                ext = 'jpg'
            elif 'image/png' in content_type or url.endswith('.png'):
                ext = 'png'
            elif 'image/webp' in content_type or url.endswith('.webp'):
                ext = 'webp'
            else:
                ext = 'jpg'  # default
            
            # Create filename
            filename = f"{product_name.lower().replace(' ', '_')}.{ext}"
            
            # Return ContentFile
            return ContentFile(response.content, name=filename)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'    Failed to download image: {str(e)}'))
            return None

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Adding garage door products...'))
        
        # Create door category
        doors_category, _ = ProductCategory.objects.get_or_create(
            slug='garage-doors',
            defaults={
                'name': 'Garage Doors',
                'name_en': 'Garage Doors',
                'description': 'Wide selection of residential and commercial garage doors',
                'icon': 'fa-door-closed',
                'order': 1,
                'is_active': True
            }
        )
        
        # Available colors for most doors
        standard_colors = """White
Almond
Sandtone
Brown"""
        
        # Available textures
        standard_textures = "Smooth, Woodgrain"
        
        # Window options
        window_options_text = """Multiple window designs available
- Plain Glass
- Frosted Glass
- Decorative Glass
- No Windows Option"""
        
        # Door products data with image URLs
        door_products = [
            {
                'name': 'Carriage House Door',
                'name_en': 'Carriage House Door',
                'brand': 'Protech',
                'image_url': 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=800',  # Carriage house style door
                'short_description': 'Classic carriage house style with premium black iron hardware',
                'description': '''The Carriage House Door combines timeless elegance with modern functionality. This premium door features authentic carriage house design with optional black iron hardware.

Available in both light and dark finishes with your choice of smooth or woodgrain texture. Perfect for homeowners seeking a sophisticated, traditional look that enhances curb appeal.

Features premium construction with multiple color options and comprehensive window selection. The door provides excellent insulation options to keep your garage comfortable year-round.''',
                'features': '''Premium Black Iron Hardware (Optional)
Available in 4 Colors (White, Almond, Sandtone, Brown)
Light or Dark Finish Options
Smooth or Woodgrain Texture
Multiple Window Styles
Insulated Options Available
Weather-Resistant Construction
Low Maintenance
Professional Installation Included''',
                'specifications': '''Panel Style: Carriage House
Material: Steel
Available Widths: 8ft, 9ft, 10ft, 16ft
Available Heights: 7ft, 8ft
Insulation: Single, Double, or Triple Layer
R-Value: Up to R-18
Warranty: Lifetime Limited Warranty''',
                'panel_style': 'carriage_house',
                'material': 'steel',
                'is_featured': True,
                'order': 1,
            },
            {
                'name': 'Lexington Panel Door - Long Panel',
                'name_en': 'Lexington Panel Door - Long Panel',
                'brand': 'Protech',
                'image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600',  # Long panel garage door
                'short_description': 'Traditional long panel design with elegant styling',
                'description': '''The Lexington Long Panel Door offers a traditional aesthetic with modern durability. This classic design features elongated panels that create a sophisticated, timeless look.

Available in both light and dark finishes with smooth or textured surfaces. The long panel design works beautifully with various architectural styles and window options.

Built with quality materials and professional craftsmanship, this door provides reliable performance and lasting beauty for your home.''',
                'features': '''Traditional Long Panel Design
Available in 4 Colors
Light or Dark Finish
Smooth or Woodgrain Texture
Compatible with Multiple Window Styles
Insulated Construction
Durable Steel Construction
Energy Efficient
Low Maintenance
Professional Installation''',
                'specifications': '''Panel Style: Long Panel (Lexington)
Material: Steel
Available Widths: 8ft, 9ft, 10ft, 16ft
Available Heights: 7ft, 8ft
Insulation: Double Layer
R-Value: R-16
Warranty: Limited Lifetime''',
                'panel_style': 'long_panel',
                'material': 'steel',
                'is_featured': True,
                'order': 2,
            },
            {
                'name': 'Lexington Panel Door - Short Panel',
                'name_en': 'Lexington Panel Door - Short Panel',
                'brand': 'Protech',
                'image_url': 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800',  # Short panel garage door
                'short_description': 'Classic short panel design with versatile styling',
                'description': '''The Lexington Short Panel Door provides a classic, versatile look that complements any home style. The short panel configuration offers a traditional appearance with contemporary functionality.

Choose from light or smooth finishes in multiple colors. This design pairs well with various window options to create your perfect custom look.

Quality construction ensures years of reliable operation while maintaining its attractive appearance.''',
                'features': '''Classic Short Panel Design
4 Color Options
Light or Smooth Finish Options
Smooth or Textured Surface
Multiple Window Choices
Insulated for Energy Efficiency
Weather Resistant
Durable Construction
Easy Maintenance
Professional Installation Included''',
                'specifications': '''Panel Style: Short Panel (Lexington)
Material: Steel
Available Widths: 8ft, 9ft, 10ft, 16ft
Available Heights: 7ft, 8ft
Insulation: Double Layer
R-Value: R-16
Warranty: Limited Lifetime''',
                'panel_style': 'short_panel',
                'material': 'steel',
                'is_featured': False,
                'order': 3,
            },
            {
                'name': 'Flush Door',
                'name_en': 'Flush Door',
                'brand': 'Protech',
                'image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800',  # Modern flush door
                'short_description': 'Clean, modern flush panel design',
                'description': '''The Flush Door offers a clean, contemporary look with its smooth, uninterrupted surface. This modern design is perfect for homeowners seeking a minimalist aesthetic.

Available in standard colors with smooth finish options. The flush design provides a sleek appearance while maintaining the durability and insulation properties you need.

Ideal for modern and contemporary home styles, this door combines style with practical performance.''',
                'features': '''Modern Flush Design
Smooth Surface
Available in 2 Textures
Multiple Color Options
Contemporary Styling
Insulated Construction
Low Maintenance
Durable Materials
Professional Installation
Clean, Minimalist Look''',
                'specifications': '''Panel Style: Flush
Material: Steel
Available Widths: 8ft, 9ft, 10ft, 16ft
Available Heights: 7ft, 8ft
Insulation: Single or Double Layer
R-Value: Up to R-16
Warranty: Limited Warranty''',
                'panel_style': 'contemporary',
                'material': 'steel',
                'is_featured': False,
                'order': 4,
            },
            {
                'name': 'Wood-Like Door',
                'name_en': 'Wood-Like Door',
                'brand': 'Protech',
                'image_url': 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=700',  # Wood texture door
                'short_description': 'Authentic wood appearance without the maintenance',
                'description': '''The Wood-Like Door delivers the beauty of natural wood with the durability of modern materials. Advanced manufacturing creates an authentic wood grain appearance that requires minimal maintenance.

Perfect for homeowners who love the warmth of wood but want the reliability of steel. Available in multiple wood-tone finishes to match your home's exterior.

Enjoy the classic elegance of wood-style doors without the ongoing upkeep and maintenance concerns.''',
                'features': '''Authentic Wood Appearance
Low Maintenance Alternative to Real Wood
Durable Steel Construction
Wood Grain Texture
Multiple Wood-Tone Colors
Insulated for Energy Efficiency
Weather Resistant
No Painting or Staining Required
Professional Installation
Long-Lasting Beauty''',
                'specifications': '''Panel Style: Wood-Like
Material: Steel with Wood Texture
Available Widths: 8ft, 9ft, 10ft, 16ft
Available Heights: 7ft, 8ft
Insulation: Double Layer
R-Value: R-16
Warranty: Limited Lifetime''',
                'panel_style': 'traditional',
                'material': 'steel',
                'is_featured': False,
                'order': 5,
            },
            {
                'name': 'Glass Door',
                'name_en': 'Glass Door',
                'brand': 'Protech',
                'image_url': 'https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=800',  # Glass garage door
                'short_description': 'Modern full-view glass garage door',
                'description': '''The Glass Door makes a stunning architectural statement with its contemporary full-view design. Featuring aluminum frames and glass panels, this door floods your garage with natural light.

Perfect for modern homes, commercial spaces, or anywhere you want to showcase your vehicles or workspace. Available with clear, frosted, or tinted glass options.

The sleek aluminum frame provides strength while the glass panels create an open, inviting atmosphere. Transform your garage into a seamless extension of your living space.''',
                'features': '''Full-View Glass Design
Aluminum Frame Construction
Natural Light Transmission
Modern Contemporary Style
Clear, Frosted, or Tinted Glass Options
Insulated Glass Available
Anodized Aluminum Frame
Low Maintenance
Custom Sizing Available
Professional Installation''',
                'specifications': '''Panel Style: Contemporary Glass
Material: Aluminum Frame with Glass Panels
Available Widths: 8ft, 9ft, 10ft, 16ft
Available Heights: 7ft, 8ft
Glass Options: Clear, Frosted, Tinted
Insulation: Insulated Glass Available
Frame: Anodized Aluminum
Warranty: Limited Warranty''',
                'panel_style': 'contemporary',
                'material': 'aluminum',
                'is_featured': True,
                'order': 6,
            },
            {
                'name': 'Modern Flush Aluminum Door',
                'name_en': 'Modern Flush Aluminum Door',
                'brand': 'Protech',
                'image_url': 'https://images.unsplash.com/photo-1523217582562-09d0def993a6?w=800',  # Aluminum modern door
                'short_description': 'Sleek aluminum door with smooth finish',
                'description': '''The Modern Flush Aluminum Door exemplifies contemporary design with its clean lines and smooth surface. Lightweight yet durable aluminum construction offers excellent longevity with minimal maintenance.

The flush design provides a sophisticated, modern appearance perfect for contemporary homes and commercial buildings. Available in popular colors including almond.

This door combines the durability of aluminum with modern aesthetics, creating a stylish entrance that stands the test of time.''',
                'features': '''Modern Flush Design
Lightweight Aluminum Construction
Smooth Finish
Contemporary Styling
Almond Color Available
Weather Resistant
Rust-Proof Material
Low Maintenance
Durable Construction
Professional Installation Included''',
                'specifications': '''Panel Style: Modern Flush
Material: Aluminum
Available Colors: Almond, White, and others
Available Widths: 8ft, 9ft, 10ft, 16ft
Available Heights: 7ft, 8ft
Finish: Smooth
Insulation: Optional
Warranty: Limited Warranty''',
                'panel_style': 'contemporary',
                'material': 'aluminum',
                'is_featured': False,
                'order': 7,
            },
        ]
        
        # Add products
        for idx, product_data in enumerate(door_products, 1):
            # Extract door specs data
            panel_style = product_data.pop('panel_style')
            material = product_data.pop('material')
            image_url = product_data.pop('image_url', None)
            
            # Create product
            product, created = Product.objects.get_or_create(
                slug=product_data['name_en'].lower().replace(' ', '-').replace('--', '-'),
                defaults={
                    **product_data,
                    'category': doors_category,
                    'product_type': 'door',
                    'is_active': True,
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Added: {product.name_en}'))
                
                # Download and save image
                if image_url and not product.image:
                    image_file = self.download_image(image_url, product.name_en)
                    if image_file:
                        product.image.save(image_file.name, image_file, save=True)
                        self.stdout.write(self.style.SUCCESS(f'  Image saved for {product.name_en}'))
                    time.sleep(0.5)  # Be nice to the server
                
                # Create door specifications
                door_spec, spec_created = DoorSpecifications.objects.get_or_create(
                    product=product,
                    defaults={
                        'panel_style': panel_style,
                        'material': material,
                        'width_options': '8ft, 9ft, 10ft, 16ft',
                        'height_options': '7ft, 8ft',
                        'insulation_type': 'double',
                        'r_value': 'R-16',
                        'color_options': standard_colors,
                        'texture_options': standard_textures,
                        'has_windows': True,
                        'window_options': window_options_text,
                        'warranty_years': 10,
                    }
                )
                
                if spec_created:
                    self.stdout.write(self.style.SUCCESS(f'  Added specifications for {product.name_en}'))
            else:
                self.stdout.write(self.style.WARNING(f'Already exists: {product.name_en}'))
        
        # Add Custom Doors category product
        custom_door_image_url = 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800'
        custom_door, created = Product.objects.get_or_create(
            slug='custom-garage-doors',
            defaults={
                'name': 'Custom Garage Doors',
                'name_en': 'Custom Garage Doors',
                'category': doors_category,
                'product_type': 'door',
                'brand': 'Protech',
                'short_description': 'Fully customized garage doors designed to your specifications',
                'description': '''Create your dream garage door with our custom design service. Choose from unlimited combinations of styles, colors, materials, windows, and hardware to perfectly match your home.

Our expert team works with you to design and build a one-of-a-kind garage door that reflects your personal style and complements your home's architecture.

Whether you want a unique wood design, special color matching, or custom hardware, we can bring your vision to life with professional craftsmanship and quality materials.''',
                'features': '''Unlimited Design Options
Custom Panel Designs
Any Color or Finish
Custom Window Configurations
Premium Hardware Selections
Wood, Steel, or Aluminum Options
Professional Design Consultation
Expert Craftsmanship
Perfect Match to Your Home
Unique One-of-a-Kind Designs''',
                'specifications': '''Style: Fully Custom
Materials: Wood, Steel, Aluminum, or Composite
Sizes: Any Custom Size
Colors: Unlimited Custom Colors
Windows: Custom Configurations
Hardware: Premium Custom Options
Insulation: As Specified
Warranty: Manufacturer's Warranty''',
                'is_featured': True,
                'is_active': True,
                'order': 0,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Added: {custom_door.name_en}'))
            
            # Download and save image for custom door
            if custom_door_image_url and not custom_door.image:
                image_file = self.download_image(custom_door_image_url, custom_door.name_en)
                if image_file:
                    custom_door.image.save(image_file.name, image_file, save=True)
                    self.stdout.write(self.style.SUCCESS(f'  Image saved for {custom_door.name_en}'))
            
            # Create door specifications for custom door
            DoorSpecifications.objects.get_or_create(
                product=custom_door,
                defaults={
                    'panel_style': 'traditional',
                    'material': 'composite',
                    'width_options': 'Any Custom Size',
                    'height_options': 'Any Custom Size',
                    'insulation_type': 'triple',
                    'r_value': 'Custom',
                    'color_options': 'Unlimited Custom Colors',
                    'texture_options': 'Any Available Texture',
                    'has_windows': True,
                    'window_options': 'Custom Window Configurations Available',
                    'warranty_years': 10,
                }
            )
        else:
            self.stdout.write(self.style.WARNING(f'Already exists: {custom_door.name_en}'))
        
        self.stdout.write(self.style.SUCCESS('\nAll door products added successfully!'))
        self.stdout.write(self.style.SUCCESS('Total products added: 8 garage doors'))
        self.stdout.write(self.style.SUCCESS('You can view products at: /admin/products/'))
        self.stdout.write(self.style.WARNING('\nNote: Product images need to be added manually through admin panel'))

