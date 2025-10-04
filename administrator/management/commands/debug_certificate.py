from django.core.management.base import BaseCommand
from administrator.models import Certificate

class Command(BaseCommand):
    help = 'Debug certificate issue'

    def handle(self, *args, **options):
        certificates = Certificate.objects.all()
        
        for cert in certificates:
            self.stdout.write(f"Certificate ID: {cert.id}")
            self.stdout.write(f"  certificate_file field: '{cert.certificate_file}'")
            self.stdout.write(f"  certificate_file is None: {cert.certificate_file is None}")
            self.stdout.write(f"  certificate_file is empty: {cert.certificate_file == ''}")
            self.stdout.write(f"  certificate_file is blank: {cert.certificate_file == '' or cert.certificate_file is None}")
            
            # Check with different filters
            is_null = Certificate.objects.filter(certificate_file__isnull=True, id=cert.id).exists()
            is_empty = Certificate.objects.filter(certificate_file='', id=cert.id).exists()
            is_blank = Certificate.objects.filter(certificate_file__isnull=True, id=cert.id).exists() or Certificate.objects.filter(certificate_file='', id=cert.id).exists()
            
            self.stdout.write(f"  Filter __isnull=True: {is_null}")
            self.stdout.write(f"  Filter ='': {is_empty}")
            self.stdout.write(f"  Is blank: {is_blank}")
            self.stdout.write("---") 