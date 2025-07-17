from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fix duplicate UUIDs in the database'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Fix Patient table
            cursor.execute("""
                UPDATE patients_patient
                SET uuid = gen_random_uuid()
                WHERE uuid IN (
                    SELECT uuid
                    FROM patients_patient
                    GROUP BY uuid
                    HAVING COUNT(*) > 1
                )
            """)
            
            # Fix other tables
            tables = [
                'patients_allergy',
                'patients_medication',
                'patients_medicalhistory',
                'patients_surgicalhistory',
                'patients_cancertype',
                'patients_cancerhistory',
                'patients_addictionhistory',
                'patients_primaryphysician',
                'patients_pharmacist'
            ]
            
            for table in tables:
                cursor.execute(f"""
                    UPDATE {table}
                    SET uuid = gen_random_uuid()
                    WHERE uuid IN (
                        SELECT uuid
                        FROM {table}
                        GROUP BY uuid
                        HAVING COUNT(*) > 1
                    )
                """)
                
            self.stdout.write(self.style.SUCCESS('Successfully fixed duplicate UUIDs')) 