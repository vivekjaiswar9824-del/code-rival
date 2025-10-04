from django.core.management.base import BaseCommand
from administrator.models import Certificate

class Command(BaseCommand):
    help = 'Check all certificates and their file status'

    def handle(self, *args, **options):
        certificates = Certificate.objects.all()
        
        if certificates:
            self.stdout.write(f"Found {certificates.count()} certificates:")
            for cert in certificates:
                self.stdout.write(f"ID: {cert.id}")
                self.stdout.write(f"  Developer: {cert.developer.name}")
                self.stdout.write(f"  Course: {cert.course.title}")
                self.stdout.write(f"  Level: {cert.level}")
                self.stdout.write(f"  File: {cert.certificate_file}")
                self.stdout.write(f"  File exists: {cert.certificate_file and cert.certificate_file.path and cert.certificate_file.storage.exists(cert.certificate_file.name)}")
                self.stdout.write("---")
        else:
            self.stdout.write("No certificates found in the database.") 