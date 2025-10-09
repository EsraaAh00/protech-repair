# services/management/commands/add_services.py
from django.core.management.base import BaseCommand
from services.models import ServiceCategory, Service


class Command(BaseCommand):
    help = 'إضافة خدمات Protech Garage Doors إلى قاعدة البيانات'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Adding services...'))
        
        # Create service categories
        repair_category, _ = ServiceCategory.objects.get_or_create(
            slug='repair-services',
            defaults={
                'name': 'Repair & Maintenance Services',
                'name_en': 'Repair & Maintenance Services',
                'description': 'All garage door repair and maintenance services',
                'icon': 'fa-tools',
                'order': 1,
                'is_active': True
            }
        )
        
        installation_category, _ = ServiceCategory.objects.get_or_create(
            slug='installation-services',
            defaults={
                'name': 'Installation Services',
                'name_en': 'Installation Services',
                'description': 'New door and equipment installation services',
                'icon': 'fa-wrench',
                'order': 2,
                'is_active': True
            }
        )
        
        # Repair services list
        repair_services = [
            {
                'title': 'Extension Springs Repair',
                'title_en': 'Extension Springs Repair',
                'short_description': 'Professional extension springs repair and replacement',
                'description': 'We provide high-quality repair and replacement services for extension springs to ensure your garage door operates smoothly and safely.',
                'icon': 'fa-spring',
            },
            {
                'title': 'Torsion Springs Repair',
                'title_en': 'Torsion Springs Repair',
                'short_description': 'Expert torsion springs repair and replacement',
                'description': 'Specialized service in repairing and replacing torsion springs with complete safety and precision.',
                'icon': 'fa-cog',
            },
            {
                'title': 'Garage Door Openers Repair',
                'title_en': 'Garage Door Openers Repair',
                'short_description': 'Repair all types of garage door openers',
                'description': 'We repair and maintain all types of electric garage door openers to keep your door functioning perfectly.',
                'icon': 'fa-door-open',
            },
            {
                'title': 'Cables Repair',
                'title_en': 'Cables Repair',
                'short_description': 'Garage door cables repair and replacement',
                'description': 'Professional repair and replacement service for damaged or worn garage door cables.',
                'icon': 'fa-link',
            },
            {
                'title': 'Rollers Repair',
                'title_en': 'Rollers Repair',
                'short_description': 'Damaged rollers replacement',
                'description': 'We provide roller replacement services to ensure smooth door movement and quiet operation.',
                'icon': 'fa-circle',
            },
            {
                'title': 'Hinges Repair',
                'title_en': 'Hinges Repair',
                'short_description': 'Hinges replacement and repair',
                'description': 'Expert repair and replacement service for damaged or broken garage door hinges.',
                'icon': 'fa-arrows-alt-h',
            },
            {
                'title': 'Damaged Sections Repair',
                'title_en': 'Damaged Sections Repair',
                'short_description': 'Repair or replace damaged door sections',
                'description': 'We repair or replace damaged sections of your garage door to restore its appearance and functionality.',
                'icon': 'fa-hammer',
            },
            {
                'title': 'Off Track Door Repair',
                'title_en': 'Off Track Door Repair',
                'short_description': 'Get your door back on track',
                'description': 'Specialized service to get off-track garage doors back to their proper position safely and efficiently.',
                'icon': 'fa-road',
            },
            {
                'title': 'Tune Ups',
                'title_en': 'Tune Ups',
                'short_description': 'Comprehensive maintenance service',
                'description': 'Regular tune-up service to keep your garage door in optimal condition and prevent future problems.',
                'icon': 'fa-tasks',
            },
        ]
        
        # Installation services list
        installation_services = [
            {
                'title': 'Remotes Installation',
                'title_en': 'Remotes Installation',
                'short_description': 'Programming and installation of garage door remotes',
                'description': 'We provide programming and installation services for garage door remotes to give you convenient access to your garage.',
                'icon': 'fa-wifi',
            },
            {
                'title': 'Key Pads Installation',
                'title_en': 'Key Pads Installation',
                'short_description': 'Installation and programming of key pads',
                'description': 'Professional installation and programming service for garage door keypads for secure and easy access.',
                'icon': 'fa-keyboard',
            },
            {
                'title': 'New Garage Door Installation',
                'title_en': 'New Garage Door Installation',
                'short_description': 'Install new garage doors with various designs',
                'description': 'We install new garage doors with a wide variety of panel designs and styles to match your home perfectly.',
                'icon': 'fa-door-closed',
            },
        ]
        
        # Common problems we solve (Features)
        common_problems = """Worn out hardware
Cable off the drums
Door won't open
Broken door parts
Door won't go up
Roller out of tracks
Door won't close
Gaps around door (bottom/side/top)
Door damaged/broken/dented"""
        
        # إضافة خدمات الإصلاح
        order = 1
        for service_data in repair_services:
            service, created = Service.objects.get_or_create(
                slug=service_data['title_en'].lower().replace(' ', '-'),
                defaults={
                    **service_data,
                    'category': repair_category,
                    'features': common_problems,
                    'order': order,
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Added: {service.title_en}'))
            else:
                self.stdout.write(self.style.WARNING(f'Already exists: {service.title_en}'))
            order += 1
        
        # إضافة خدمات التركيب
        for service_data in installation_services:
            service, created = Service.objects.get_or_create(
                slug=service_data['title_en'].lower().replace(' ', '-'),
                defaults={
                    **service_data,
                    'category': installation_category,
                    'features': common_problems,
                    'order': order,
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Added: {service.title_en}'))
            else:
                self.stdout.write(self.style.WARNING(f'Already exists: {service.title_en}'))
            order += 1
        
        # Add main comprehensive service
        main_service, created = Service.objects.get_or_create(
            slug='service-and-repair',
            defaults={
                'title': 'Service & Repair',
                'title_en': 'Service & Repair',
                'category': repair_category,
                'short_description': 'At Protech Garage Doors we are highly skilled in any garage door repair & installation',
                'description': '''At Protech Garage Doors we are highly skilled in any garage door repair & installation.

We have over 15 years of experience and are certain we can solve any of your garage door problems.

Feel free to contact us if you have any questions. Call us today for your free estimate!

Need a new garage door? Choose from a variety of panel designs & styles & we'll install it for you!''',
                'features': '''Extension Springs
Torsion springs
Openers
Cables
Rollers
Hinges
Damaged sections
Off track door
All garage door openers
Tune ups
Remotes
Key pads

Common Problems We Solve:
Worn out hardware
Cable off the drums
Door won't open
Broken door parts
Door won't go up
Roller out of tracks
Door won't close
Gaps around door (bottom/side/top)
Door damaged/broken/dented''',
                'icon': 'fa-tools',
                'order': 0,
                'is_featured': True,
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Added main service: {main_service.title_en}'))
        else:
            self.stdout.write(self.style.WARNING(f'Main service already exists: {main_service.title_en}'))
        
        self.stdout.write(self.style.SUCCESS('\nAll services added successfully!'))
        self.stdout.write(self.style.SUCCESS('You can view services at: /admin/services/'))

