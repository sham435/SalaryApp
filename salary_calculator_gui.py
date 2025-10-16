import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import datetime
from datetime import timedelta
import calendar
import sqlite3
import os
from typing import List, Dict, Optional
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import webbrowser

class LaborSalaryCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jatan Jewellery - Salary Management System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')

        # Initialize calculator
        self.calculator = EnhancedLaborSalaryCalculator()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        self.create_dashboard_tab()
        self.create_labor_profiles_tab()
        self.create_salary_calculation_tab()
        self.create_reports_tab()
        self.create_certificates_tab()

        # Load initial data
        self.refresh_labor_profiles()

    def create_dashboard_tab(self):
        """Create dashboard tab with overview"""
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="Dashboard")

        # Header
        header_frame = ttk.LabelFrame(self.dashboard_tab, text="Jatan Jewellery - Salary Management")
        header_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(header_frame, text="Salary Management System",
                 font=('Arial', 16, 'bold')).pack(pady=10)

        # Quick stats
        stats_frame = ttk.LabelFrame(self.dashboard_tab, text="Quick Statistics")
        stats_frame.pack(fill='x', padx=10, pady=10)

        # Stats will be populated dynamically
        self.stats_labels = {}
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill='x', padx=10, pady=10)

        stats = [
            ("Total Laborers", "0"),
            ("This Month's Payroll", "AED 0"),
            ("Pending Calculations", "0"),
            ("Recent Activity", "None")
        ]

        for i, (title, value) in enumerate(stats):
            frame = ttk.Frame(stats_grid)
            frame.grid(row=0, column=i, padx=20, pady=10, sticky='ew')
            ttk.Label(frame, text=title, font=('Arial', 10)).pack()
            label = ttk.Label(frame, text=value, font=('Arial', 12, 'bold'))
            label.pack()
            self.stats_labels[title] = label

        # Recent activity
        activity_frame = ttk.LabelFrame(self.dashboard_tab, text="Recent Activity")
        activity_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.activity_tree = ttk.Treeview(activity_frame, columns=('Date', 'Activity', 'Details'), show='headings', height=8)
        self.activity_tree.heading('Date', text='Date')
        self.activity_tree.heading('Activity', text='Activity')
        self.activity_tree.heading('Details', text='Details')
        self.activity_tree.column('Date', width=120)
        self.activity_tree.column('Activity', width=150)
        self.activity_tree.column('Details', width=300)
        self.activity_tree.pack(fill='both', expand=True, padx=10, pady=10)

        self.update_dashboard()

    def create_labor_profiles_tab(self):
        """Create labor profiles management tab"""
        self.profiles_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.profiles_tab, text="Labor Profiles")

        # Input frame
        input_frame = ttk.LabelFrame(self.profiles_tab, text="Add/Edit Labor Profile")
        input_frame.pack(fill='x', padx=10, pady=10)

        # Form fields
        fields = [
            ("Name", "name_entry"),
            ("Daily Wage (AED)", "wage_entry"),
            ("Position", "position_entry"),
            ("Contact Info", "contact_entry"),
            ("Overtime Rate", "overtime_entry")
        ]

        for i, (label, var_name) in enumerate(fields):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='w')
            entry = ttk.Entry(input_frame)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
            setattr(self, var_name, entry)

        # Set default overtime rate
        self.overtime_entry.insert(0, "1.5")

        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Add Profile", command=self.add_labor_profile).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Update Profile", command=self.update_labor_profile).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Profile", command=self.delete_labor_profile).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_profile_form).pack(side='left', padx=5)

        input_frame.columnconfigure(1, weight=1)

        # Profiles list
        list_frame = ttk.LabelFrame(self.profiles_tab, text="Labor Profiles")
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.profiles_tree = ttk.Treeview(list_frame, columns=('ID', 'Name', 'Daily Wage', 'Position', 'Contact', 'Overtime Rate'), show='headings', height=15)

        columns = {
            'ID': 50,
            'Name': 150,
            'Daily Wage': 100,
            'Position': 120,
            'Contact': 150,
            'Overtime Rate': 100
        }

        for col, width in columns.items():
            self.profiles_tree.heading(col, text=col)
            self.profiles_tree.column(col, width=width)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.profiles_tree.yview)
        self.profiles_tree.configure(yscrollcommand=scrollbar.set)

        self.profiles_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Bind selection
        self.profiles_tree.bind('<<TreeviewSelect>>', self.on_profile_select)

    def create_salary_calculation_tab(self):
        """Create salary calculation tab"""
        self.calculation_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.calculation_tab, text="Salary Calculation")

        # Left frame - Inputs
        input_frame = ttk.LabelFrame(self.calculation_tab, text="Salary Calculation Parameters")
        input_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        # Labor selection
        ttk.Label(input_frame, text="Select Laborer:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.labor_combo = ttk.Combobox(input_frame, state='readonly')
        self.labor_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # Period selection
        ttk.Label(input_frame, text="Year:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.year_combo = ttk.Combobox(input_frame, values=[str(year) for year in range(2020, 2031)])
        self.year_combo.set(str(datetime.datetime.now().year))
        self.year_combo.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(input_frame, text="Month:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.month_combo = ttk.Combobox(input_frame, values=[f"{i:02d} - {calendar.month_name[i]}" for i in range(1, 13)])
        self.month_combo.set(f"{datetime.datetime.now().month:02d} - {calendar.month_name[datetime.datetime.now().month]}")
        self.month_combo.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        # Calculation options
        options_frame = ttk.LabelFrame(input_frame, text="Calculation Options")
        options_frame.grid(row=3, column=0, columnspan=2, sticky='ew', padx=5, pady=10)

        self.include_weekends = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Include Weekends", variable=self.include_weekends).pack(anchor='w', padx=5, pady=2)

        self.custom_wage_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Use Custom Daily Wage", variable=self.custom_wage_var).pack(anchor='w', padx=5, pady=2)

        ttk.Label(options_frame, text="Custom Daily Wage (AED):").pack(anchor='w', padx=5, pady=2)
        self.custom_wage_entry = ttk.Entry(options_frame)
        self.custom_wage_entry.pack(fill='x', padx=5, pady=2)

        ttk.Label(options_frame, text="Overtime Hours:").pack(anchor='w', padx=5, pady=2)
        self.overtime_hours_entry = ttk.Entry(options_frame)
        self.overtime_hours_entry.insert(0, "0")
        self.overtime_hours_entry.pack(fill='x', padx=5, pady=2)

        ttk.Label(options_frame, text="Hours per Day:").pack(anchor='w', padx=5, pady=2)
        self.hours_per_day_entry = ttk.Entry(options_frame)
        self.hours_per_day_entry.insert(0, "8")
        self.hours_per_day_entry.pack(fill='x', padx=5, pady=2)

        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Calculate Salary", command=self.calculate_salary).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Save Calculation", command=self.save_salary_calculation).pack(side='left', padx=5)

        input_frame.columnconfigure(1, weight=1)

        # Right frame - Results
        results_frame = ttk.LabelFrame(self.calculation_tab, text="Calculation Results")
        results_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        # Summary results
        self.summary_text = tk.Text(results_frame, height=10, width=50)
        self.summary_text.pack(fill='both', expand=True, padx=5, pady=5)

        # Working dates
        dates_frame = ttk.LabelFrame(results_frame, text="Working Dates")
        dates_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.dates_tree = ttk.Treeview(dates_frame, columns=('Date', 'Day', 'Type'), show='headings', height=8)
        self.dates_tree.heading('Date', text='Date')
        self.dates_tree.heading('Day', text='Day')
        self.dates_tree.heading('Type', text='Type')
        self.dates_tree.column('Date', width=100)
        self.dates_tree.column('Day', width=100)
        self.dates_tree.column('Type', width=100)

        scrollbar = ttk.Scrollbar(dates_frame, orient='vertical', command=self.dates_tree.yview)
        self.dates_tree.configure(yscrollcommand=scrollbar.set)

        self.dates_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_reports_tab(self):
        """Create reports tab"""
        self.reports_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_tab, text="Reports")

        # Controls frame
        controls_frame = ttk.LabelFrame(self.reports_tab, text="Report Parameters")
        controls_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(controls_frame, text="Year:").grid(row=0, column=0, padx=5, pady=5)
        self.report_year_combo = ttk.Combobox(controls_frame, values=[str(year) for year in range(2020, 2031)])
        self.report_year_combo.set(str(datetime.datetime.now().year))
        self.report_year_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(controls_frame, text="Month:").grid(row=0, column=2, padx=5, pady=5)
        self.report_month_combo = ttk.Combobox(controls_frame, values=[f"{i:02d} - {calendar.month_name[i]}" for i in range(1, 13)])
        self.report_month_combo.set(f"{datetime.datetime.now().month:02d} - {calendar.month_name[datetime.datetime.now().month]}")
        self.report_month_combo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(controls_frame, text="Laborer:").grid(row=0, column=4, padx=5, pady=5)
        self.report_labor_combo = ttk.Combobox(controls_frame, state='readonly')
        self.report_labor_combo.grid(row=0, column=5, padx=5, pady=5)

        button_frame = ttk.Frame(controls_frame)
        button_frame.grid(row=1, column=0, columnspan=6, pady=10)

        ttk.Button(button_frame, text="Generate Summary Report", command=self.generate_summary_report).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Generate Detailed Report", command=self.generate_detailed_report).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Export to Excel", command=self.export_to_excel).pack(side='left', padx=5)

        # Report display
        report_frame = ttk.LabelFrame(self.reports_tab, text="Report Results")
        report_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.report_tree = ttk.Treeview(report_frame, show='headings', height=20)

        scrollbar_x = ttk.Scrollbar(report_frame, orient='horizontal', command=self.report_tree.xview)
        scrollbar_y = ttk.Scrollbar(report_frame, orient='vertical', command=self.report_tree.yview)
        self.report_tree.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)

        self.report_tree.pack(side='left', fill='both', expand=True)
        scrollbar_y.pack(side='right', fill='y')
        scrollbar_x.pack(side='bottom', fill='x')

    def create_certificates_tab(self):
        """Create salary certificates tab"""
        self.certificates_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.certificates_tab, text="Salary Certificates")

        # Certificate generation
        cert_frame = ttk.LabelFrame(self.certificates_tab, text="Generate Salary Certificate")
        cert_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(cert_frame, text="Select Laborer:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.cert_labor_combo = ttk.Combobox(cert_frame, state='readonly')
        self.cert_labor_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(cert_frame, text="Passport Number:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.passport_entry = ttk.Entry(cert_frame)
        self.passport_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(cert_frame, text="Emirates ID:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.emirates_id_entry = ttk.Entry(cert_frame)
        self.emirates_id_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(cert_frame, text="Position:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.cert_position_entry = ttk.Entry(cert_frame)
        self.cert_position_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(cert_frame, text="Join Date:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.join_date_entry = ttk.Entry(cert_frame)
        self.join_date_entry.grid(row=4, column=1, padx=5, pady=5, sticky='ew')

        # Salary components
        salary_frame = ttk.LabelFrame(cert_frame, text="Salary Components (AED)")
        salary_frame.grid(row=5, column=0, columnspan=2, sticky='ew', padx=5, pady=10)

        ttk.Label(salary_frame, text="Basic Salary:").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        self.basic_salary_entry = ttk.Entry(salary_frame)
        self.basic_salary_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')

        ttk.Label(salary_frame, text="Housing Allowance:").grid(row=1, column=0, padx=5, pady=2, sticky='w')
        self.housing_entry = ttk.Entry(salary_frame)
        self.housing_entry.insert(0, "0")
        self.housing_entry.grid(row=1, column=1, padx=5, pady=2, sticky='ew')

        ttk.Label(salary_frame, text="Transportation Allowance:").grid(row=2, column=0, padx=5, pady=2, sticky='w')
        self.transport_entry = ttk.Entry(salary_frame)
        self.transport_entry.insert(0, "0")
        self.transport_entry.grid(row=2, column=1, padx=5, pady=2, sticky='ew')

        ttk.Label(salary_frame, text="Other Allowances:").grid(row=3, column=0, padx=5, pady=2, sticky='w')
        self.other_allowances_entry = ttk.Entry(salary_frame)
        self.other_allowances_entry.insert(0, "0")
        self.other_allowances_entry.grid(row=3, column=1, padx=5, pady=2, sticky='ew')

        ttk.Label(salary_frame, text="Deductions:").grid(row=4, column=0, padx=5, pady=2, sticky='w')
        self.deductions_entry = ttk.Entry(salary_frame)
        self.deductions_entry.insert(0, "0")
        self.deductions_entry.grid(row=4, column=1, padx=5, pady=2, sticky='ew')

        # Buttons
        cert_button_frame = ttk.Frame(cert_frame)
        cert_button_frame.grid(row=6, column=0, columnspan=2, pady=10)

        ttk.Button(cert_button_frame, text="Generate Certificate", command=self.generate_certificate).pack(side='left', padx=5)
        ttk.Button(cert_button_frame, text="Load from Calculation", command=self.load_from_calculation).pack(side='left', padx=5)

        cert_frame.columnconfigure(1, weight=1)
        salary_frame.columnconfigure(1, weight=1)

    def refresh_labor_profiles(self):
        """Refresh labor profiles in all comboboxes"""
        profiles = self.calculator.view_labor_profiles()
        labor_names = profiles['name'].tolist() if not profiles.empty else []

        self.labor_combo['values'] = labor_names
        self.report_labor_combo['values'] = ['All'] + labor_names
        self.cert_labor_combo['values'] = labor_names

        if labor_names:
            self.labor_combo.set(labor_names[0])
            self.report_labor_combo.set('All')
            self.cert_labor_combo.set(labor_names[0])

        # Update profiles tree
        self.profiles_tree.delete(*self.profiles_tree.get_children())
        for _, profile in profiles.iterrows():
            self.profiles_tree.insert('', 'end', values=(
                profile['id'],
                profile['name'],
                f"AED {profile['base_daily_wage']:.2f}",
                profile['position'],
                profile['contact_info'],
                profile['overtime_rate']
            ))

    def add_labor_profile(self):
        """Add new labor profile"""
        name = self.name_entry.get().strip()
        wage = self.wage_entry.get().strip()
        position = self.position_entry.get().strip()
        contact = self.contact_entry.get().strip()
        overtime_rate = self.overtime_entry.get().strip()

        if not name or not wage:
            messagebox.showerror("Error", "Name and Daily Wage are required!")
            return

        try:
            wage_float = float(wage)
            overtime_float = float(overtime_rate) if overtime_rate else 1.5

            self.calculator.add_labor_profile(name, wage_float, position, contact, overtime_float)
            self.refresh_labor_profiles()
            self.clear_profile_form()
            self.add_activity("Profile Added", f"Added labor profile: {name}")
            self.update_dashboard()

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for wage and overtime rate!")

    def update_labor_profile(self):
        """Update selected labor profile"""
        selection = self.profiles_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a profile to update!")
            return

        item = self.profiles_tree.item(selection[0])
        profile_id = item['values'][0]

        name = self.name_entry.get().strip()
        wage = self.wage_entry.get().strip()
        position = self.position_entry.get().strip()
        contact = self.contact_entry.get().strip()
        overtime_rate = self.overtime_entry.get().strip()

        if not name or not wage:
            messagebox.showerror("Error", "Name and Daily Wage are required!")
            return

        try:
            conn = sqlite3.connect(self.calculator.db_name)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE labor_profiles
                SET name=?, base_daily_wage=?, position=?, contact_info=?, overtime_rate=?
                WHERE id=?
            ''', (name, float(wage), position, contact, float(overtime_rate), profile_id))

            conn.commit()
            conn.close()

            self.refresh_labor_profiles()
            self.clear_profile_form()
            self.add_activity("Profile Updated", f"Updated labor profile: {name}")
            self.update_dashboard()

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for wage and overtime rate!")

    def delete_labor_profile(self):
        """Delete selected labor profile"""
        selection = self.profiles_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a profile to delete!")
            return

        item = self.profiles_tree.item(selection[0])
        profile_name = item['values'][1]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {profile_name}?"):
            profile_id = item['values'][0]

            conn = sqlite3.connect(self.calculator.db_name)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM labor_profiles WHERE id=?', (profile_id,))
            conn.commit()
            conn.close()

            self.refresh_labor_profiles()
            self.clear_profile_form()
            self.add_activity("Profile Deleted", f"Deleted labor profile: {profile_name}")
            self.update_dashboard()

    def clear_profile_form(self):
        """Clear profile form fields"""
        self.name_entry.delete(0, tk.END)
        self.wage_entry.delete(0, tk.END)
        self.position_entry.delete(0, tk.END)
        self.contact_entry.delete(0, tk.END)
        self.overtime_entry.delete(0, tk.END)
        self.overtime_entry.insert(0, "1.5")

    def on_profile_select(self, event):
        """Handle profile selection"""
        selection = self.profiles_tree.selection()
        if not selection:
            return

        item = self.profiles_tree.item(selection[0])
        values = item['values']

        self.clear_profile_form()

        self.name_entry.insert(0, values[1])
        self.wage_entry.insert(0, values[2].replace('AED ', ''))
        self.position_entry.insert(0, values[3])
        self.contact_entry.insert(0, values[4])
        self.overtime_entry.delete(0, tk.END)
        self.overtime_entry.insert(0, values[5])

    def calculate_salary(self):
        """Calculate salary based on parameters"""
        labor_name = self.labor_combo.get()
        if not labor_name:
            messagebox.showerror("Error", "Please select a laborer!")
            return

        try:
            year = int(self.year_combo.get())
            month = int(self.month_combo.get().split(' - ')[0])

            # Get labor profile for base wage
            profiles = self.calculator.view_labor_profiles()
            labor_profile = profiles[profiles['name'] == labor_name].iloc[0]
            base_wage = labor_profile['base_daily_wage']

            # Determine daily wage
            if self.custom_wage_var.get():
                daily_wage = float(self.custom_wage_entry.get())
            else:
                daily_wage = base_wage

            include_weekends = self.include_weekends.get()
            overtime_hours = float(self.overtime_hours_entry.get() or 0)
            hours_per_day = float(self.hours_per_day_entry.get() or 8)
            overtime_rate = labor_profile['overtime_rate']

            # Calculate salary
            monthly_data = self.calculator.calculate_monthly_salary(
                labor_name=labor_name,
                daily_wage=daily_wage,
                year=year,
                month=month,
                hours_per_day=hours_per_day,
                overtime_per_day=overtime_hours,
                overtime_rate=overtime_rate,
                include_weekends=include_weekends
            )

            # Store for potential saving
            self.current_calculation = monthly_data

            # Display results
            self.display_calculation_results(monthly_data)
            self.add_activity("Salary Calculated", f"Calculated salary for {labor_name} - {calendar.month_name[month]} {year}")

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def display_calculation_results(self, monthly_data):
        """Display calculation results"""
        summary = monthly_data['summary']

        result_text = f"""
SALARY CALCULATION RESULTS
==========================
Labor Name: {monthly_data['labor_name']}
Period: {monthly_data['month_name']} {monthly_data['year']}
Total Working Days: {monthly_data['total_working_days']}

SALARY BREAKDOWN:
-----------------
Regular Pay: AED {summary['total_regular_pay']:,.2f}
Overtime Pay: AED {summary['total_overtime_pay']:,.2f}
Weekend Bonus: AED {summary['total_weekend_bonus']:,.2f}
Holiday Bonus: AED {summary['total_holiday_bonus']:,.2f}
Other Allowances: AED {summary['total_allowances']:,.2f}
Deductions: AED {summary['total_deductions']:,.2f}
─────────────────────────
TOTAL SALARY: AED {summary['total_salary']:,.2f}

DAY TYPE SUMMARY:
-----------------
"""
        for day_type, count in monthly_data['day_type_summary'].items():
            result_text += f"{day_type}: {count} days\n"

        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, result_text)

        # Update working dates tree
        self.dates_tree.delete(*self.dates_tree.get_children())
        for daily in monthly_data['daily_salaries']:
            self.dates_tree.insert('', 'end', values=(
                daily['date_str'],
                daily['day_name'],
                daily['day_type']
            ))

    def save_salary_calculation(self):
        """Save current calculation to database"""
        if not hasattr(self, 'current_calculation'):
            messagebox.showerror("Error", "No calculation to save! Please calculate first.")
            return

        self.calculator.save_salary_records(self.current_calculation)
        self.add_activity("Salary Saved", f"Saved salary for {self.current_calculation['labor_name']}")
        self.update_dashboard()

    def generate_summary_report(self):
        """Generate summary report"""
        try:
            year = int(self.report_year_combo.get())
            month = int(self.report_month_combo.get().split(' - ')[0])
            labor_name = self.report_labor_combo.get()
            labor_name = None if labor_name == 'All' else labor_name

            report = self.calculator.generate_summary_report(year, month)

            if report.empty:
                messagebox.showinfo("No Data", "No records found for the specified period.")
                return

            # Update treeview
            self.update_report_tree(report)
            self.add_activity("Report Generated", f"Summary report for {calendar.month_name[month]} {year}")

        except ValueError:
            messagebox.showerror("Error", "Invalid year or month!")

    def generate_detailed_report(self):
        """Generate detailed report"""
        try:
            year = int(self.report_year_combo.get())
            month = int(self.report_month_combo.get().split(' - ')[0])
            labor_name = self.report_labor_combo.get()
            labor_name = None if labor_name == 'All' else labor_name

            report = self.calculator.generate_detailed_report(year, month, labor_name)

            if report.empty:
                messagebox.showinfo("No Data", "No records found for the specified period.")
                return

            # Update treeview
            self.update_report_tree(report)
            self.add_activity("Report Generated", f"Detailed report for {calendar.month_name[month]} {year}")

        except ValueError:
            messagebox.showerror("Error", "Invalid year or month!")

    def update_report_tree(self, df):
        """Update report treeview with dataframe"""
        # Clear existing columns and data
        for col in self.report_tree['columns']:
            self.report_tree.heading(col, text="")
        self.report_tree.delete(*self.report_tree.get_children())

        # Set new columns
        self.report_tree['columns'] = list(df.columns)
        for col in df.columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=100)

        # Add data
        for _, row in df.iterrows():
            self.report_tree.insert('', 'end', values=tuple(row))

    def export_to_excel(self):
        """Export current report to Excel"""
        # Get data from treeview
        items = self.report_tree.get_children()
        if not items:
            messagebox.showerror("Error", "No data to export!")
            return

        # Get columns and data
        columns = self.report_tree['columns']
        data = []
        for item in items:
            data.append(self.report_tree.item(item)['values'])

        # Create DataFrame and export
        df = pd.DataFrame(data, columns=columns)

        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )

        if filename:
            df.to_excel(filename, index=False)
            messagebox.showinfo("Success", f"Report exported to {filename}")
            self.add_activity("Report Exported", f"Exported report to Excel")

    def generate_certificate(self):
        """Generate salary certificate PDF"""
        labor_name = self.cert_labor_combo.get()
        passport = self.passport_entry.get().strip()
        emirates_id = self.emirates_id_entry.get().strip()
        position = self.cert_position_entry.get().strip()
        join_date = self.join_date_entry.get().strip()

        if not all([labor_name, passport, emirates_id, position, join_date]):
            messagebox.showerror("Error", "Please fill all required fields!")
            return

        try:
            basic_salary = float(self.basic_salary_entry.get() or 0)
            housing = float(self.housing_entry.get() or 0)
            transport = float(self.transport_entry.get() or 0)
            other_allowances = float(self.other_allowances_entry.get() or 0)
            deductions = float(self.deductions_entry.get() or 0)

            gross_salary = basic_salary + housing + transport + other_allowances
            net_salary = gross_salary - deductions

            # Generate PDF
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=f"Salary_Certificate_{labor_name.replace(' ', '_')}.pdf"
            )

            if filename:
                self.create_pdf_certificate(
                    filename, labor_name, passport, emirates_id, position, join_date,
                    basic_salary, housing, transport, other_allowances,
                    deductions, gross_salary, net_salary
                )

                messagebox.showinfo("Success", f"Salary certificate generated: {filename}")
                self.add_activity("Certificate Generated", f"Generated certificate for {labor_name}")

                # Open PDF
                if messagebox.askyesno("Open Certificate", "Would you like to open the certificate?"):
                    webbrowser.open(filename)

        except ValueError:
            messagebox.showerror("Error", "Please enter valid salary amounts!")

    def create_pdf_certificate(self, filename, labor_name, passport, emirates_id, position, join_date,
                             basic_salary, housing, transport, other_allowances,
                             deductions, gross_salary, net_salary):
        """Create PDF salary certificate"""
        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1
        )

        elements.append(Paragraph("JATAN JEWELLERY FZ.C", title_style))
        elements.append(Paragraph("Ajman Free Zone C1-1F-SF5235", styles['Normal']))
        elements.append(Paragraph("sales@jatanjewellery.com | https://jatanjewellery.com", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Certificate header
        elements.append(Paragraph("Salary Certificate", styles['Heading2']))
        elements.append(Paragraph(f"Trade License Number: 41778", styles['Normal']))
        elements.append(Paragraph(f"Date: {datetime.datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Employee information
        info_text = f"""
        To Whom It May Concern<br/>
        This is to certify that Mr./Ms. <b>{labor_name}</b>, holding Passport No.: <b>{passport}</b>/
        Emirates ID: <b>{emirates_id}</b>, is employed with Jatan Jewellery - AFZ as a
        <b>{position}</b> since <b>{join_date}</b>.
        """
        elements.append(Paragraph(info_text, styles['Normal']))
        elements.append(Spacer(1, 20))

        # Salary table
        salary_data = [
            ['Salary Component', 'Amount (AED)'],
            ['Basic Salary', f'{basic_salary:,.2f}'],
            ['Housing Allowance', f'{housing:,.2f}'],
            ['Transportation Allowance', f'{transport:,.2f}'],
            ['Other Allowances', f'{other_allowances:,.2f}'],
            ['Gross Salary', f'{gross_salary:,.2f}'],
            ['Deductions (if any)', f'{deductions:,.2f}'],
            ['Net Salary', f'{net_salary:,.2f}']
        ]

        table = Table(salary_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
        elements.append(Spacer(1, 30))

        # Footer
        footer_text = """
        This certificate is issued upon the request of the employee.
        The above information is true and correct to the best of our knowledge.
        """
        elements.append(Paragraph(footer_text, styles['Normal']))
        elements.append(Spacer(1, 40))

        elements.append(Paragraph("Authorized Signatory:", styles['Normal']))
        elements.append(Paragraph("Name: Ms. Akshita Badekhaniya Bhushan Kumar Sain", styles['Normal']))
        elements.append(Paragraph("Designation: Individual Shareholder", styles['Normal']))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Signature & Company Stamp", styles['Normal']))

        doc.build(elements)

    def load_from_calculation(self):
        """Load salary data from latest calculation"""
        if not hasattr(self, 'current_calculation'):
            messagebox.showerror("Error", "No recent calculation found!")
            return

        labor_name = self.current_calculation['labor_name']
        total_salary = self.current_calculation['summary']['total_salary']

        # Set basic salary as total from calculation
        self.basic_salary_entry.delete(0, tk.END)
        self.basic_salary_entry.insert(0, str(total_salary))

        # Set labor name if matches
        if labor_name in self.cert_labor_combo['values']:
            self.cert_labor_combo.set(labor_name)

        messagebox.showinfo("Success", "Salary data loaded from recent calculation!")

    def add_activity(self, activity, details):
        """Add activity to dashboard"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.activity_tree.insert('', 0, values=(timestamp, activity, details))

        # Keep only last 10 activities
        if len(self.activity_tree.get_children()) > 10:
            self.activity_tree.delete(self.activity_tree.get_children()[-1])

    def update_dashboard(self):
        """Update dashboard statistics"""
        profiles = self.calculator.view_labor_profiles()
        total_laborers = len(profiles)

        # Calculate this month's payroll
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month

        try:
            report = self.calculator.generate_summary_report(current_year, current_month)
            total_payroll = report['total_salary'].sum() if not report.empty else 0
        except:
            total_payroll = 0

        self.stats_labels["Total Laborers"].config(text=str(total_laborers))
        self.stats_labels["This Month's Payroll"].config(text=f"AED {total_payroll:,.2f}")
        self.stats_labels["Pending Calculations"].config(text="0")  # Could be enhanced
        self.stats_labels["Recent Activity"].config(text=f"{len(self.activity_tree.get_children())} activities")

# Enhanced Labor Salary Calculator Class
class EnhancedLaborSalaryCalculator:
    def __init__(self, db_name='labor_salary.db'):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Labor profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS labor_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                base_daily_wage REAL NOT NULL,
                hourly_rate REAL NOT NULL,
                position TEXT,
                contact_info TEXT,
                overtime_rate REAL DEFAULT 1.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Salary records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS salary_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                labor_name TEXT NOT NULL,
                date DATE NOT NULL,
                day_type TEXT DEFAULT 'Weekday',
                daily_wage REAL NOT NULL,
                hours_worked REAL DEFAULT 8,
                regular_hours REAL DEFAULT 8,
                overtime_hours REAL DEFAULT 0,
                overtime_rate REAL DEFAULT 1.5,
                weekend_bonus REAL DEFAULT 0,
                holiday_bonus REAL DEFAULT 0,
                other_allowances REAL DEFAULT 0,
                deductions REAL DEFAULT 0,
                total_salary REAL NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def add_labor_profile(self, name, base_daily_wage, position="", contact_info="", overtime_rate=1.5):
        """Add labor profile"""
        hourly_rate = base_daily_wage / 8

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO labor_profiles
                (name, base_daily_wage, hourly_rate, position, contact_info, overtime_rate)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, base_daily_wage, hourly_rate, position, contact_info, overtime_rate))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def view_labor_profiles(self):
        """View all labor profiles"""
        conn = sqlite3.connect(self.db_name)
        df = pd.read_sql_query('SELECT * FROM labor_profiles ORDER BY name', conn)
        conn.close()
        return df

    def get_working_dates(self, year, month, include_weekends=False):
        """Get working dates for a month"""
        working_dates = []
        num_days = calendar.monthrange(year, month)[1]

        for day in range(1, num_days + 1):
            current_date = datetime.date(year, month, day)
            is_weekend = current_date.weekday() >= 5

            if include_weekends or not is_weekend:
                day_type = "Weekend" if is_weekend else "Weekday"
                working_dates.append({
                    'date': current_date,
                    'date_str': current_date.strftime('%Y-%m-%d'),
                    'day_name': current_date.strftime('%A'),
                    'day_type': day_type,
                    'is_weekend': is_weekend,
                    'is_holiday': False
                })

        return working_dates

    def calculate_monthly_salary(self, labor_name, daily_wage, year, month,
                                hours_per_day=8, overtime_per_day=0, overtime_rate=1.5,
                                include_weekends=False, other_allowances=0, deductions=0):
        """Calculate monthly salary"""
        working_dates = self.get_working_dates(year, month, include_weekends)
        daily_salaries = []

        total_regular_pay = 0
        total_overtime_pay = 0
        total_weekend_bonus = 0
        total_holiday_bonus = 0

        hourly_rate = daily_wage / 8

        for date_info in working_dates:
            # Regular pay
            regular_pay = daily_wage

            # Overtime pay
            overtime_pay = overtime_per_day * hourly_rate * overtime_rate

            # Weekend bonus
            weekend_bonus = daily_wage * 0.5 if date_info['is_weekend'] else 0

            total_daily = regular_pay + overtime_pay + weekend_bonus + other_allowances - deductions

            daily_salaries.append({
                'labor_name': labor_name,
                'date': date_info['date'],
                'date_str': date_info['date_str'],
                'day_type': date_info['day_type'],
                'day_name': date_info['day_name'],
                'daily_wage': daily_wage,
                'hours_worked': hours_per_day,
                'regular_hours': min(hours_per_day, 8),
                'overtime_hours': max(hours_per_day - 8, 0) + overtime_per_day,
                'overtime_rate': overtime_rate,
                'regular_pay': regular_pay,
                'overtime_pay': overtime_pay,
                'weekend_bonus': weekend_bonus,
                'holiday_bonus': 0,
                'other_allowances': other_allowances,
                'deductions': deductions,
                'total_salary': total_daily
            })

            total_regular_pay += regular_pay
            total_overtime_pay += overtime_pay
            total_weekend_bonus += weekend_bonus

        total_salary = total_regular_pay + total_overtime_pay + total_weekend_bonus + total_holiday_bonus

        # Day type summary
        day_type_summary = {}
        for salary in daily_salaries:
            day_type = salary['day_type']
            day_type_summary[day_type] = day_type_summary.get(day_type, 0) + 1

        return {
            'labor_name': labor_name,
            'year': year,
            'month': month,
            'month_name': calendar.month_name[month],
            'total_working_days': len(working_dates),
            'day_type_summary': day_type_summary,
            'daily_salaries': daily_salaries,
            'summary': {
                'total_regular_pay': total_regular_pay,
                'total_overtime_pay': total_overtime_pay,
                'total_weekend_bonus': total_weekend_bonus,
                'total_holiday_bonus': total_holiday_bonus,
                'total_allowances': other_allowances * len(working_dates),
                'total_deductions': deductions * len(working_dates),
                'total_salary': total_salary
            }
        }

    def save_salary_records(self, monthly_data):
        """Save salary records to database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        for daily_salary in monthly_data['daily_salaries']:
            cursor.execute('''
                INSERT INTO salary_records
                (labor_name, date, day_type, daily_wage, hours_worked, regular_hours,
                 overtime_hours, overtime_rate, weekend_bonus, holiday_bonus,
                 other_allowances, deductions, total_salary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                daily_salary['labor_name'],
                daily_salary['date_str'],
                daily_salary['day_type'],
                daily_salary['daily_wage'],
                daily_salary['hours_worked'],
                daily_salary['regular_hours'],
                daily_salary['overtime_hours'],
                daily_salary['overtime_rate'],
                daily_salary['weekend_bonus'],
                daily_salary['holiday_bonus'],
                daily_salary['other_allowances'],
                daily_salary['deductions'],
                daily_salary['total_salary']
            ))

        conn.commit()
        conn.close()

    def generate_summary_report(self, year, month):
        """Generate summary report"""
        conn = sqlite3.connect(self.db_name)

        query = '''
            SELECT
                labor_name,
                COUNT(*) as working_days,
                SUM(regular_hours) as total_regular_hours,
                SUM(overtime_hours) as total_overtime_hours,
                SUM(daily_wage * regular_hours / 8) as total_regular_pay,
                SUM(overtime_hours * (daily_wage / 8) * overtime_rate) as total_overtime_pay,
                SUM(weekend_bonus) as total_weekend_bonus,
                SUM(holiday_bonus) as total_holiday_bonus,
                SUM(other_allowances) as total_allowances,
                SUM(deductions) as total_deductions,
                SUM(total_salary) as total_salary
            FROM salary_records
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
            GROUP BY labor_name
            ORDER BY total_salary DESC
        '''

        df = pd.read_sql_query(query, conn, params=[str(year), f"{month:02d}"])
        conn.close()

        return df

    def generate_detailed_report(self, year, month, labor_name=None):
        """Generate detailed report"""
        conn = sqlite3.connect(self.db_name)

        query = '''
            SELECT labor_name, date, day_type, daily_wage, hours_worked, regular_hours,
                   overtime_hours, overtime_rate, weekend_bonus, holiday_bonus,
                   other_allowances, deductions, total_salary
            FROM salary_records
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
        '''
        params = [str(year), f"{month:02d}"]

        if labor_name:
            query += ' AND labor_name = ?'
            params.append(labor_name)

        query += ' ORDER BY date, labor_name'

        df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        return df

if __name__ == "__main__":
    root = tk.Tk()
    app = LaborSalaryCalculatorGUI(root)
    root.mainloop()

