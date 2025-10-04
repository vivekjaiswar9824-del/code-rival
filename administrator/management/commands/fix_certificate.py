from django.core.management.base import BaseCommand
from administrator.models import Certificate
from administrator.views import generate_certificate_pdf

class Command(BaseCommand):
    help = 'Fix existing certificate by generating its file'

    def handle(self, *args, **options):
        # Get the certificate without a file (check for both null and empty string)
        certificate = Certificate.objects.filter(certificate_file__isnull=True).first()
        if not certificate:
            certificate = Certificate.objects.filter(certificate_file='').first()
        
        if certificate:
            self.stdout.write(f"Fixing certificate ID: {certificate.id}")
            self.stdout.write(f"Developer: {certificate.developer.name}")
            self.stdout.write(f"Course: {certificate.course.title}")
            self.stdout.write(f"Level: {certificate.level}")
            
            # Generate the certificate file
            result = generate_certificate_pdf(certificate)
            
            if result:
                self.stdout.write(self.style.SUCCESS("Certificate file generated successfully!"))
                certificate.refresh_from_db()
                self.stdout.write(f"File path: {certificate.certificate_file}")
            else:
                self.stdout.write(self.style.ERROR("Certificate file generation failed!"))
        else:
            self.stdout.write("No certificates found without files to fix.") 