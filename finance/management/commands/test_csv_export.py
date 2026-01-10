"""
Script to test the Student Fees CSV Export functionality

This script demonstrates how to access and use the CSV export feature.
You can run this manually or integrate it into automated reporting workflows.
"""

from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from finance.views import student_fees_csv_export

User = get_user_model()


class Command(BaseCommand):
    help = 'Test the student fees CSV export functionality'

    def handle(self, *args, **options):
        # Create a mock request
        factory = RequestFactory()
        
        # Create GET request to the CSV export endpoint
        request = factory.get('/finance/reports/students-fees-csv/')
        
        # Get an admin user for testing
        try:
            admin_user = User.objects.filter(role='ADMIN').first()
            if not admin_user:
                admin_user = User.objects.filter(role='SUPER_ADMIN').first()
            
            if not admin_user:
                self.stdout.write(
                    self.style.ERROR('No admin user found. Please create an admin user first.')
                )
                return
            
            # Attach user to request
            request.user = admin_user
            
            # Call the view
            self.stdout.write('Generating CSV report...')
            response = student_fees_csv_export(request)
            
            # Check response
            if response.status_code == 200:
                # Save to file for inspection
                with open('student_fees_test_export.csv', 'wb') as f:
                    f.write(response.content)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        'CSV report generated successfully!\n'
                        'File saved as: student_fees_test_export.csv\n'
                        f'Content length: {len(response.content)} bytes'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to generate report. Status code: {response.status_code}'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during test: {str(e)}')
            )
            import traceback
            self.stdout.write(traceback.format_exc())


# Alternative: Direct URL test
"""
To test via browser or curl:

1. Login as admin user
2. Navigate to: http://localhost:8000/finance/invoices/
3. Click the "Export CSV" button
4. Or directly visit: http://localhost:8000/finance/reports/students-fees-csv/

Via curl:
curl -H "Cookie: sessionid=YOUR_SESSION_ID" \
     http://localhost:8000/finance/reports/students-fees-csv/ \
     -o student_fees_report.csv
"""
