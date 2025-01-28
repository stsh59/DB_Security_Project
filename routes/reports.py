from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
import pymysql

bp = Blueprint('reports', __name__)

@bp.route('/reports')
@login_required
def reports():
    if current_user.role != 'admin':
        flash('Access restricted to admin only', 'danger')
        return redirect(url_for('dashboard.index'))

    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='9808311242Ab@',
            database='hospitaldb'
        )
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # All report queries
        reports_queries = {
            '1': {
                'query': '''SELECT FirstName, LastName, PatientID
                            FROM hospitaldb.patients
                            WHERE AdmissionDate = '2022-04-10' AND DATEDIFF(DischargeDate, AdmissionDate) >= 10''',
                'heading': 'Patients Admitted on 2022-04-10 and Stayed for 10+ Days'
            },
            '2': {
                'query': '''SELECT DISTINCT d.DoctorID, d.FirstName, d.LastName
                            FROM hospitaldb.doctors d
                            WHERE d.DoctorID IN (
                                SELECT DISTINCT v.DoctorID
                                FROM hospitaldb.visits v
                                INNER JOIN (
                                    SELECT FirstName, LastName, PatientID
                                    FROM hospitaldb.patients
                                    WHERE AdmissionDate = '2022-04-10' AND DATEDIFF(DischargeDate, AdmissionDate) >= 10
                                ) AS p ON v.PatientID = p.PatientID
                                WHERE v.DepartmentID = 1
                            )''',
                'heading': 'Doctors Who Visited Patients Admitted on 2022-04-10 and Stayed for 10+ Days'
            },
            '3': {
                'query': '''SELECT p.PatientID, p.FirstName AS PatientFirstName, p.LastName AS PatientLastName,
                                   d.DoctorID, d.FirstName AS DoctorFirstName, d.LastName AS DoctorLastName
                            FROM hospitaldb.patients p
                            JOIN hospitaldb.surgeries s ON p.PatientID = s.PatientID
                            JOIN hospitaldb.doctors d ON s.DoctorID = d.DoctorID
                            WHERE MONTH(s.SurgeryDate) IN (3, 4, 5)
                              AND d.FirstName = "Dr. Emily" AND d.LastName = "Brown"''',
                'heading': 'Patients Who Got Surgery in Spring by Dr. Emily Brown'
            },
            '4': {
                'query': '''SELECT DISTINCT v.ServiceID, s.ServiceName
                            FROM hospitaldb.visits v
                            JOIN hospitaldb.services s ON v.ServiceID = s.ServiceID
                            WHERE v.DepartmentID = 1''',
                'heading': 'Services Received in Inpatient Department'
            },
            '5': {
                'query': '''SELECT s.ServiceName
                            FROM hospitaldb.doctors d
                            JOIN hospitaldb.servicedr sd ON d.DoctorID = sd.DoctorID
                            JOIN hospitaldb.services s ON sd.ServiceID = s.ServiceID
                            WHERE d.FirstName = "Dr. Emily" AND d.LastName = "Brown"''',
                'heading': 'Services Provided by Dr. Emily Brown'
            },
            '6': {
                'query': '''SELECT SUM(s.Cost) AS TotalCost
                            FROM hospitaldb.visits v
                            JOIN hospitaldb.patients p ON v.PatientID = p.PatientID
                            JOIN hospitaldb.doctors d ON v.DoctorID = d.DoctorID
                            JOIN hospitaldb.services s ON v.ServiceID = s.ServiceID
                            JOIN hospitaldb.departments dep ON v.DepartmentID = dep.DepartmentID
                            WHERE v.DepartmentID = 1
                              AND p.FirstName = "Bob" AND p.LastName = "Johnson"''',
                'heading': 'Total Cost of Services for Bob Johnson in Inpatient Department'
            },
        }

        reports_data = []
        for report_id, report_details in reports_queries.items():
            cursor.execute(report_details['query'])
            data = cursor.fetchall()
            reports_data.append({
                'heading': report_details['heading'],
                'data': data
            })

        connection.close()
        return render_template('report.html', reports_data=reports_data)

    except Exception as e:
        print(f"Error in reports route: {e}")  # Debugging log
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('dashboard.index'))
