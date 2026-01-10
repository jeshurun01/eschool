# Student Fees CSV Export with Filters

## Overview
Interactive export feature that generates a comprehensive CSV report of students with their class information and detailed fee breakdown. **Now includes a powerful filtering interface** to customize exports by classes, fee types, and specific students.

## Features

### Interactive Filter Interface
Before downloading the CSV, users can access a comprehensive filter page where they can:

1. **Filter by Classes** - Select specific classrooms to include in the report
2. **Filter by Fee Types** - Choose which fee types to include as columns
3. **Select Specific Students** - Pick individual students (with search functionality)
4. **Combine Filters** - Use multiple filters together for precise exports

### CSV Report Format
The exported CSV file contains the following columns:

1. **Matricule** - Student registration number
2. **Étudiant** - Student full name
3. **Classe** - Current class/classroom
4. **[Dynamic Fee Types]** - One column for each selected fee type (e.g., Scolarité, Inscription, Transport, etc.)
5. **Total Facturé** - Total amount invoiced
6. **Total Payé** - Total amount paid
7. **Solde Restant** - Remaining balance

### Summary Row
At the bottom of the report, a summary row is added with:
- Total amounts per fee type across all filtered students
- Grand total of all invoices
- Grand total of all payments
- Total remaining balance

## Usage

### Accessing the Export

The CSV export can be accessed from:

1. **Finance Dashboard** - Invoice List page
   - URL: `/finance/invoices/`
   - Look for the green "Export CSV" button in the top action bar
   - Click to open the filter interface

2. **Filter Interface**
   - URL: `/finance/reports/students-fees-export/`
   - Interactive page with all filtering options
   - Preview of available classes, fee types, and students

3. **Direct Export** (bypassing filters)
   - URL: `/finance/reports/students-fees-csv/`
   - Optional parameters: `?classes=1,2&fee_types=3,4&students=5,6`

### Using the Filter Interface

#### Step-by-Step Guide

1. **Access the Filter Page**
   - Click "Export CSV" button from the invoice list
   - Or navigate directly to `/finance/reports/students-fees-export/`

2. **Select Classes** (Optional)
   - Check individual classes you want to include
   - Use "Select All/Deselect All" to toggle all at once
   - Leave empty to include all classes

3. **Select Fee Types** (Optional)
   - Check the fee types you want as columns in the CSV
   - Use "Select All/Deselect All" for quick selection
   - Leave empty to include all fee types

4. **Select Specific Students** (Optional)
   - Use the search box to find students by name, matricule, or class
   - Check individual students to include only them
   - Use "Select All/Deselect All" to toggle all visible students
   - Leave empty to include all students (filtered by class if selected)

5. **Download**
   - Click "Télécharger le CSV" button
   - CSV file downloads immediately with applied filters

### Filter Behaviors

#### Class Filter
- **When selected**: Only students from checked classes are included
- **When empty**: All students from all classes are included

#### Fee Type Filter
- **When selected**: CSV columns only show checked fee types
- **When empty**: All fee types appear as columns

#### Student Filter
- **When selected**: Only checked students are included
- **When empty**: All students (respecting class filter) are included

#### Combined Filters
- All filters work together using AND logic
- Example: Select "6ème A" class + "Scolarité" fee type = Only students from 6ème A with only Scolarité column

### Permissions
- Requires `finance_required` permission
- Available to: Finance Manager, Admin, Super Admin roles

## Technical Details

### View Functions
Located in: `finance/views.py`

1. **`student_fees_export_filters(request)`**
   - Displays the filter interface
   - Loads available classes, fee types, and students
   - Renders the filter template

2. **`student_fees_csv_export(request)`**
   - Generates the CSV file
   - Processes filter parameters from GET request
   - Returns downloadable CSV response

### URL Configuration
Located in: `finance/urls.py`

- Filter Interface: `reports/students-fees-export/` → `student_fees_export_filters`
- CSV Download: `reports/students-fees-csv/` → `student_fees_csv_export`

### Data Processing

1. **Filter Parsing**: 
   - Classes: `request.GET.getlist('classes')` → List of class IDs
   - Fee Types: `request.GET.getlist('fee_types')` → List of fee type IDs
   - Students: `request.GET.getlist('students')` → List of student IDs

2. **Student Query**: 
   - Base: All active students
   - Apply class filter if provided
   - Apply student filter if provided
   - Order by class and name

3. **Fee Type Query**:
   - Apply fee type filter if provided
   - Default: All fee types
   - Order by name

4. **Invoice Calculation**: For each filtered student:
   - Retrieves all invoices for the academic year
   - Groups invoice items by selected fee types
   - Calculates totals, paid amounts, and balances

5. **Aggregation**: Computes grand totals across filtered data

### CSV Encoding
- UTF-8 with BOM (Byte Order Mark) for proper Excel compatibility
- Filename: `student_fees_report.csv`
- Content-Type: `text/csv; charset=utf-8`

## Example Output

### Filtered by Class (6ème A) and Fee Types (Scolarité, Transport)

```csv
Matricule,Étudiant,Classe,Scolarité,Transport,Total Facturé,Total Payé,Solde Restant
STU2024001,Jean Dupont,6ème A,150000.00,15000.00,165000.00,165000.00,0.00
STU2024002,Marie Martin,6ème A,150000.00,15000.00,165000.00,100000.00,65000.00

,TOTAL GÉNÉRAL,,300000.00,30000.00,330000.00,265000.00,65000.00
```

## Use Cases

1. **Class-Specific Reports**: Export fees for a single class (e.g., 6ème A)
2. **Fee Type Analysis**: Compare only specific fees across students (e.g., only Transport)
3. **Selected Students**: Create reports for scholarship recipients or specific groups
4. **Financial Reporting**: Full reports with all data for accounting
5. **Payment Follow-up**: Filter by class to identify outstanding balances per classroom
6. **Management Reports**: Custom combinations for different stakeholders

## UI Features

### Search Functionality
- Real-time search for students by name, matricule, or class
- Instant filtering of student list as you type
- Case-insensitive search

### Bulk Selection
- "Select All / Deselect All" buttons for each filter section
- Quickly select or clear entire groups
- Works with search results (only visible students)

### Visual Feedback
- Hover effects on checkboxes
- Color-coded sections
- Clear labels and descriptions
- Confirmation prompt when exporting without filters

## Future Enhancements

Potential improvements:
- [x] Interactive filter interface
- [x] Class filtering
- [x] Fee type filtering  
- [x] Student selection with search
- [ ] Save filter presets for quick access
- [ ] Date range filters (invoice date, payment date)
- [ ] Filter by payment status (paid, partial, overdue)
- [ ] Export format selection (CSV, Excel, PDF)
- [ ] Email scheduled reports with saved filters
- [ ] Add graphs/charts in Excel export
- [ ] Filter by level instead of just classrooms

## Related Features

- Invoice Management: [finance/views.py](../finance/views.py)
- Daily Financial Reports: [DAILY_FINANCIAL_REPORT_SYSTEM.md](DAILY_FINANCIAL_REPORT_SYSTEM.md)
- Fee Structure Management: [finance/models.py](../finance/models.py)

## Notes

- Report respects RBAC permissions
- Only shows data for active students
- Performance optimized with select_related() and prefetch_related()
- Large datasets (>1000 students) may take a few seconds to generate
- Filters are applied server-side for security
- No filters selected = all data exported (with confirmation)
