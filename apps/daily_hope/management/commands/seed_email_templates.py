from django.core.management.base import BaseCommand
from apps.daily_hope.models import EmailTemplate
from apps.daily_hope.content import GET_HOPE_DROPS_CONTENT
from common.utils import visit_site_html

class Command(BaseCommand):
    help = 'Seeds the EmailTemplate model with content from content.py'

    def handle(self, *args, **options):
        self.stdout.write('Seeding email templates...')
        
        for day, content in GET_HOPE_DROPS_CONTENT.items():
            subject = f"Day {day} of your Hope Journey: {content['title']}"
            
            # HTML content with premium styling (copied from tasks.py logic)
            html_content = f"""
    <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.8; color: #2d3748; background-color: #f7fafc; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);">
                <!-- Header Image -->
                <div style="width: 100%; height: 200px; overflow: hidden;">
                    <img src="{content['image_url']}" alt="Daily Hope Day {day}" style="width: 100%; height: 100%; object-fit: cover;">
                </div>

                <div style="padding: 40px;">
                    <div style="text-transform: uppercase; letter-spacing: 0.1em; color: #a0aec0; font-weight: 700; font-size: 12px; margin-bottom: 8px;">Day {day}</div>
                    <h2 style="color: #2d3748; margin-top: 0; font-size: 28px; line-height: 1.2;">{content['title']}</h2>
                    
                    <div style="color: #4a5568; font-size: 16px; margin-bottom: 24px; white-space: pre-wrap;">{content['description']}</div>
                    
                    <!-- Verse Callout -->
                    <div style="background-color: #fffaf0; padding: 24px; border-left: 4px solid #ed8936; margin: 32px 0; border-radius: 4px;">
                        <p style="font-style: italic; margin: 0; color: #2d3748; font-size: 18px; line-height: 1.6;">{content['verse']}</p>
                    </div>

                    <div style="color: #4a5568; font-size: 16px; margin-bottom: 32px; white-space: pre-wrap;">{content.get('outro', '')}</div>

                    <!-- Reflection Section -->
                    <div style="margin-top: 40px; padding: 24px; background-color: #ebf8ff; border-radius: 12px;">
                        <h4 style="margin-top: 0; color: #2b6cb0; text-transform: uppercase; font-size: 13px; letter-spacing: 0.05em;">Take a moment to reflect</h4>
                        <p style="margin-bottom: 0; color: #2c5282; font-size: 16px;">{content.get('reflection', '')}</p>
                    </div>

                    <!-- Prayer Section -->
                    <div style="margin-top: 24px; padding: 24px; background-color: #f0fff4; border-radius: 12px;">
                        <h4 style="margin-top: 0; color: #2f855a; text-transform: uppercase; font-size: 13px; letter-spacing: 0.05em;">Simple Prayer</h4>
                        <p style="margin-bottom: 0; color: #276749; font-size: 16px; font-style: italic;">{content.get('prayer', '')}</p>
                    </div>

                    <div style="margin-top: 48px; border-top: 1px solid #edf2f7; padding-top: 32px;">
                        <p style="margin-bottom: 4px; color: #4a5568;">{content.get('sign_off', 'Hope begins here,')}</p>
                        <p style="margin-top: 0; font-weight: 700; color: #2d3748;">HopeBegins Team</p>
                    </div>

                    <div style="margin-top: 32px; font-size: 13px; color: #a0aec0;">
                        <p style="margin-bottom: 8px;">More from HopeBegins:</p>
                        <div style="display: flex; flex-direction: column; gap: 8px;">
                            <a href="https://hopebegins.today/give-hope" style="color: #ed8936; text-decoration: none;">• Support HopeBegins</a>
                            <a href="https://hopebegins.today/prayers" style="color: #ed8936; text-decoration: none;">• Share your prayer requests</a>
                        </div>
                    </div>
                </div>

                {visit_site_html('/')}

                <div style="background-color: #edf2f7; padding: 24px; text-align: center; font-size: 12px; color: #718096;">
                    <p style="margin: 0;">You are receiving this because you signed up for the 21-day Hope Journey.</p>
                </div>
            </div>
        </body>
    </html>
    """
            
            EmailTemplate.objects.get_or_create(
                day_number=day,
                defaults={
                    'subject': subject,
                    'html_content': html_content
                }
            )
            self.stdout.write(f'Created template for Day {day}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded email templates'))
