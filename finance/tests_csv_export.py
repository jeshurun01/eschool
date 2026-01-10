"""
Test script to demonstrate the filtered CSV export functionality

This shows how the filtering works with different parameters.
"""

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from finance.views import student_fees_export_filters, student_fees_csv_export
from finance.models import FeeType, Invoice, InvoiceItem
from accounts.models import Student
from academic.models import AcademicYear, ClassRoom, Level

User = get_user_model()


class StudentFeesExportTest(TestCase):
    """
    Test cases for the student fees CSV export with filters
    """
    
    def setUp(self):
        """Set up test data"""
        self.factory = RequestFactory()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            password='testpass123',
            role='ADMIN',
            is_staff=True
        )
        
        # Create academic year
        self.academic_year = AcademicYear.objects.create(
            name='2025-2026',
            is_current=True
        )
        
        # Create levels and classrooms
        self.level = Level.objects.create(name='6ème', order=1)
        self.classroom1 = ClassRoom.objects.create(
            name='6ème A',
            level=self.level,
            capacity=30
        )
        self.classroom2 = ClassRoom.objects.create(
            name='6ème B',
            level=self.level,
            capacity=30
        )
        
        # Create fee types
        self.fee_type1 = FeeType.objects.create(
            name='Scolarité',
            is_mandatory=True
        )
        self.fee_type2 = FeeType.objects.create(
            name='Transport',
            is_mandatory=False
        )
    
    def test_filter_interface_loads(self):
        """Test that the filter interface loads correctly"""
        request = self.factory.get('/finance/reports/students-fees-export/')
        request.user = self.admin_user
        
        response = student_fees_export_filters(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Classes', response.content)
        self.assertIn(b'Types de Frais', response.content)
    
    def test_csv_export_with_class_filter(self):
        """Test CSV export filtered by class"""
        request = self.factory.get(
            '/finance/reports/students-fees-csv/',
            {'classes': [self.classroom1.id]}
        )
        request.user = self.admin_user
        
        response = student_fees_csv_export(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
    
    def test_csv_export_with_fee_type_filter(self):
        """Test CSV export filtered by fee types"""
        request = self.factory.get(
            '/finance/reports/students-fees-csv/',
            {'fee_types': [self.fee_type1.id]}
        )
        request.user = self.admin_user
        
        response = student_fees_csv_export(request)
        
        self.assertEqual(response.status_code, 200)
        # Should only include the selected fee type
        self.assertIn('Scolarité'.encode('utf-8'), response.content)
    
    def test_csv_export_all_filters(self):
        """Test CSV export with multiple filters combined"""
        request = self.factory.get(
            '/finance/reports/students-fees-csv/',
            {
                'classes': [self.classroom1.id],
                'fee_types': [self.fee_type1.id, self.fee_type2.id]
            }
        )
        request.user = self.admin_user
        
        response = student_fees_csv_export(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Scolarité'.encode('utf-8'), response.content)
        self.assertIn('Transport'.encode('utf-8'), response.content)


# Manual test instructions
"""
To manually test the filtering interface:

1. Start the development server:
   python manage.py runserver

2. Login as admin user

3. Navigate to:
   http://localhost:8000/finance/reports/students-fees-export/

4. Test different scenarios:
   a) Select specific classes only
   b) Select specific fee types only
   c) Select specific students only
   d) Combine multiple filters
   e) Export with no filters (all data)

5. Verify the downloaded CSV contains only the filtered data

Expected behavior:
- Classes filter: Only students from selected classes
- Fee Types filter: Only columns for selected fee types
- Students filter: Only selected students
- No filters: All students and all fee types
"""
