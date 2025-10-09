# inquiries/management/commands/add_sample_works.py
from django.core.management.base import BaseCommand
from inquiries.models import RecentWork, Review
from services.models import Service


class Command(BaseCommand):
    help = 'Add sample recent works and reviews'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Adding sample recent works...'))
        
        # Get some services
        try:
            springs_service = Service.objects.get(slug='extension-springs-repair')
            opener_service = Service.objects.get(slug='garage-door-openers-repair')
            installation_service = Service.objects.get(slug='new-garage-door-installation')
        except Service.DoesNotExist:
            self.stdout.write(self.style.WARNING('Services not found. Please run add_services first.'))
            return
        
        # Sample recent works
        sample_works = [
            {
                'title': 'Residential Garage Door Installation',
                'description': 'Complete installation of a new residential garage door with modern design. Included new opener system and smart remote controls. Customer was extremely satisfied with the quick and professional service.',
                'service': installation_service,
                'is_featured': True,
                'order': 1,
            },
            {
                'title': 'Spring Replacement Service',
                'description': 'Emergency spring replacement for a broken torsion spring. Our team responded within 2 hours and completed the repair efficiently. The door is now operating smoothly and safely.',
                'service': springs_service,
                'is_featured': True,
                'order': 2,
            },
            {
                'title': 'Garage Door Opener Upgrade',
                'description': 'Upgraded old garage door opener to a new smart opener with WiFi connectivity. Customer can now control their garage door from anywhere using their smartphone.',
                'service': opener_service,
                'is_featured': False,
                'order': 3,
            },
            {
                'title': 'Commercial Garage Door Repair',
                'description': 'Repaired commercial garage door at a local business. Fixed off-track issues and replaced worn rollers. Minimal downtime for the business operations.',
                'service': None,
                'is_featured': False,
                'order': 4,
            },
            {
                'title': 'Custom Wood Garage Door',
                'description': 'Installed beautiful custom wood garage door for luxury home. Perfect match with home architecture. Includes insulation and high-end opener system.',
                'service': installation_service,
                'is_featured': True,
                'order': 5,
            },
        ]
        
        # Sample reviews for each work
        sample_reviews = [
            # Reviews for work 1
            [
                {
                    'customer_name': 'John Smith',
                    'customer_email': 'john.smith@example.com',
                    'rating': 5,
                    'review_text': 'Excellent service! The team was professional, on time, and did a fantastic job. Highly recommend!',
                    'is_approved': True,
                },
                {
                    'customer_name': 'Sarah Johnson',
                    'customer_email': 'sarah.j@example.com',
                    'rating': 5,
                    'review_text': 'Very happy with my new garage door. The installation was quick and clean. Great value for money.',
                    'is_approved': True,
                },
            ],
            # Reviews for work 2
            [
                {
                    'customer_name': 'Mike Davis',
                    'customer_email': 'mike.davis@example.com',
                    'rating': 5,
                    'review_text': 'Fast emergency service! They came within hours and fixed my broken spring. Professional and affordable.',
                    'is_approved': True,
                },
                {
                    'customer_name': 'Lisa Brown',
                    'customer_email': 'lisa.b@example.com',
                    'rating': 4,
                    'review_text': 'Good service and reasonable pricing. The technician was knowledgeable and friendly.',
                    'is_approved': True,
                },
                {
                    'customer_name': 'Tom Wilson',
                    'customer_email': 'tom.w@example.com',
                    'rating': 5,
                    'review_text': 'Outstanding work! My garage door works perfectly now. Thank you!',
                    'is_approved': True,
                },
            ],
            # Reviews for work 3
            [
                {
                    'customer_name': 'Jennifer Martinez',
                    'customer_email': 'jen.martinez@example.com',
                    'rating': 5,
                    'review_text': 'Love my new smart opener! Being able to control it from my phone is amazing. Installation was seamless.',
                    'is_approved': True,
                },
            ],
            # Reviews for work 4
            [
                {
                    'customer_name': 'Robert Taylor',
                    'customer_email': 'robert.t@example.com',
                    'rating': 5,
                    'review_text': 'Fixed our commercial door quickly with minimal disruption to business. Very professional team.',
                    'is_approved': True,
                },
                {
                    'customer_name': 'Amanda Lee',
                    'customer_email': 'amanda.lee@example.com',
                    'rating': 4,
                    'review_text': 'Good repair work. The door is working well now. Would use their service again.',
                    'is_approved': True,
                },
            ],
            # Reviews for work 5
            [
                {
                    'customer_name': 'David Anderson',
                    'customer_email': 'david.a@example.com',
                    'rating': 5,
                    'review_text': 'Absolutely beautiful custom door! The craftsmanship is outstanding. Worth every penny!',
                    'is_approved': True,
                },
                {
                    'customer_name': 'Michelle White',
                    'customer_email': 'michelle.w@example.com',
                    'rating': 5,
                    'review_text': 'The custom wood door looks amazing! Perfect match for our home. Excellent work!',
                    'is_approved': True,
                },
                {
                    'customer_name': 'James Harris',
                    'customer_email': 'james.h@example.com',
                    'rating': 5,
                    'review_text': 'High quality installation and beautiful door. Very satisfied with the result!',
                    'is_approved': True,
                },
            ],
        ]
        
        # Add works and reviews
        for idx, work_data in enumerate(sample_works):
            work, created = RecentWork.objects.get_or_create(
                title=work_data['title'],
                defaults=work_data
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Added: {work.title}'))
                
                # Add reviews for this work
                if idx < len(sample_reviews):
                    for review_data in sample_reviews[idx]:
                        review = Review.objects.create(
                            recent_work=work,
                            **review_data
                        )
                    self.stdout.write(self.style.SUCCESS(f'  Added {len(sample_reviews[idx])} reviews'))
            else:
                self.stdout.write(self.style.WARNING(f'Already exists: {work.title}'))
        
        self.stdout.write(self.style.SUCCESS('\nAll sample works and reviews added successfully!'))
        self.stdout.write(self.style.SUCCESS('Note: You need to add images manually through admin panel.'))
        self.stdout.write(self.style.SUCCESS('Access at: /admin/inquiries/recentwork/'))

