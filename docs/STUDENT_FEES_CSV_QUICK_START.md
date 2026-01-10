# Student Fees CSV Export - Quick Start Guide

## 🚀 Quick Access

**From Invoice List Page:**
1. Go to Finance → Invoices (`/finance/invoices/`)
2. Click the green **"Export CSV"** button
3. You'll be taken to the filter interface

**Direct Access:**
- Navigate to `/finance/reports/students-fees-export/`

---

## 📋 Filter Interface Overview

The filter page has **3 main sections**:

### 1️⃣ Classes Section
- See all available classrooms grouped by level
- Check individual classes or use "Select All/Deselect All"
- **Use Case**: Export fees for specific classes only

**Example:**
```
✓ 6ème A
✓ 6ème B
☐ 5ème A
☐ 5ème B
```
Result: Only students from 6ème A and 6ème B

---

### 2️⃣ Types de Frais (Fee Types)
- Select which fee types to include as columns
- Check individual types or use "Select All/Deselect All"
- **Use Case**: Analyze specific fee categories only

**Example:**
```
✓ Scolarité
✓ Transport
☐ Cantine
☐ Inscription
```
Result: CSV will only have Scolarité and Transport columns

---

### 3️⃣ Étudiants (Students) - Optional
- Select specific students for the report
- Use the **search box** to find students quickly
- Search by: Name, Matricule, or Class
- Check individual students or use "Select All/Deselect All"
- **Use Case**: Custom reports for specific students

**Example:**
Search: "Dupont"
```
✓ Jean Dupont (STU2024001) • 6ème A
✓ Marie Dupont (STU2024015) • 5ème A
```
Result: Only these two students in the CSV

---

## 🎯 Common Use Cases

### Use Case 1: Single Class Report
**Scenario**: Teacher needs fee report for their class

**Steps:**
1. Select: ✓ 6ème A (under Classes)
2. Leave Fee Types empty (all types)
3. Leave Students empty (all students in class)
4. Click "Télécharger le CSV"

**Result:** All students from 6ème A with all fee types

---

### Use Case 2: Transport Fee Analysis
**Scenario**: Admin wants to see who pays for transport

**Steps:**
1. Leave Classes empty (all classes)
2. Select: ✓ Transport (under Fee Types)
3. Leave Students empty (all students)
4. Click "Télécharger le CSV"

**Result:** All students with only Transport column showing

---

### Use Case 3: Scholarship Students Report
**Scenario**: Finance manager needs report for specific scholarship recipients

**Steps:**
1. Leave Classes empty
2. Leave Fee Types empty (all types)
3. Use search to find students, check each one
4. Click "Télécharger le CSV"

**Result:** Only selected students with all fee details

---

### Use Case 4: Complete Financial Overview
**Scenario**: Principal needs full school financial report

**Steps:**
1. Leave all filters empty
2. Click "Télécharger le CSV"
3. Confirm "Export all data"

**Result:** All students, all classes, all fee types

---

## 💡 Pro Tips

### Tip 1: Search Smart
The student search is **instant and flexible**:
- Search by partial name: "mar" finds "Marie Martin"
- Search by matricule: "STU2024" finds all 2024 students
- Search by class: "6ème" finds all 6ème students

### Tip 2: Use "Select All" Wisely
After searching, click "Select All" to select only **visible** students:
1. Search: "6ème"
2. Click "Select All"
3. Only 6ème students are selected

### Tip 3: Combine Filters
Mix and match for precise reports:
- **Classes + Fee Types**: Specific fees for specific classes
- **Classes + Students**: Validate student is in selected class
- **Fee Types + Students**: Specific fees for specific students

### Tip 4: Reset When Needed
Click **"Réinitialiser"** (Reset) button to clear all selections and start fresh

---

## 📊 Understanding the CSV Output

### Header Row
```csv
Matricule, Étudiant, Classe, [Selected Fee Types...], Total Facturé, Total Payé, Solde Restant
```

### Data Rows
Each row = One student with their fee breakdown

### Summary Row (Bottom)
```csv
, TOTAL GÉNÉRAL, , [Totals per fee type...], Grand Total, Total Paid, Total Balance
```

---

## ⚠️ Important Notes

1. **No Filters = All Data**
   - If you don't select anything, you'll get a confirmation prompt
   - This exports ALL students and ALL fees

2. **Active Students Only**
   - Inactive/archived students are automatically excluded
   - Graduated students with `is_active=False` won't appear

3. **Current Academic Year**
   - Report uses the current academic year by default
   - Invoice data is filtered by current academic year

4. **Excel Compatible**
   - CSV uses UTF-8 with BOM
   - Opens correctly in Excel with proper encoding
   - Accented characters display correctly

---

## 🔐 Permissions

Required role: **Finance Manager**, **Admin**, or **Super Admin**

If you don't see the "Export CSV" button, contact your administrator.

---

## 🐛 Troubleshooting

### Problem: CSV doesn't download
**Solution:** Check that you have permission and try again

### Problem: Empty CSV file
**Solution:** 
- Check if students exist in selected classes
- Verify students have invoices for current academic year
- Try without filters to see if any data exists

### Problem: Characters look wrong in Excel
**Solution:** 
- The CSV is already UTF-8 with BOM
- If issues persist, try: Data → From Text → UTF-8

### Problem: Wrong students appear
**Solution:**
- Review selected classes - students are filtered by class
- Check if students moved between classes recently

---

## 📞 Need Help?

Contact the Finance Department or System Administrator for:
- Custom report formats
- Additional filter options
- Scheduled automated reports
- Integration with accounting systems
