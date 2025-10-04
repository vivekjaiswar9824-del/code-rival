from django.core.management.base import BaseCommand
from administrator.models import Certificate, User, Course
from administrator.views import generate_certificate_pdf

class Command(BaseCommand):
    help = 'Test certificate generation'

    def handle(self, *args, **options):
        # Get the first certificate that doesn't have a file
        certificate = Certificate.objects.filter(certificate_file__isnull=True).first()
        
        if certificate:
            self.stdout.write(f"Testing certificate generation for certificate ID: {certificate.id}")
            self.stdout.write(f"Developer: {certificate.developer.name}")
            self.stdout.write(f"Course: {certificate.course.title}")
            self.stdout.write(f"Level: {certificate.level}")
            
            # Try to generate the certificate
            result = generate_certificate_pdf(certificate)
            
            if result:
                self.stdout.write(self.style.SUCCESS("Certificate generated successfully!"))
                certificate.refresh_from_db()
                self.stdout.write(f"File path: {certificate.certificate_file}")
            else:
                self.stdout.write(self.style.ERROR("Certificate generation failed!"))
        else:
            self.stdout.write("No certificates found without files to test.") 