from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import (
    College, Department, StudentProfile, Company, Job, 
    Application, SystemConfiguration
)
from django.utils import timezone
from datetime import date, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate sample data for testing'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate sample data...'))
        
        # Create system configurations
        self.create_system_configs()
        
        # Create colleges
        college = self.create_college()
        
        # Create departments
        departments = self.create_departments(college)
        
        # Create companies
        companies = self.create_companies()
        
        # Create users
        users = self.create_users()
        
        # Create student profiles
        students = self.create_student_profiles(users, college, departments)
        
        # Create jobs
        jobs = self.create_jobs(companies, college, departments, users)
        
        # Create applications
        self.create_applications(jobs, students)
        
        self.stdout.write(self.style.SUCCESS('Sample data populated successfully!'))
    
    def create_system_configs(self):
        """Create system configuration entries"""
        configs = [
            ('SITE_NAME', 'CampusConnect', 'Name of the platform'),
            ('DEFAULT_CGPA_THRESHOLD', '6.5', 'Default minimum CGPA for job applications'),
            ('EMAIL_NOTIFICATIONS_ENABLED', 'true', 'Enable email notifications'),
            ('SMS_NOTIFICATIONS_ENABLED', 'false', 'Enable SMS notifications'),
            ('MAX_APPLICATIONS_PER_STUDENT', '10', 'Maximum applications per student'),
        ]
        
        for key, value, description in configs:
            config, created = SystemConfiguration.objects.get_or_create(
                key=key,
                defaults={'value': value, 'description': description}
            )
            if created:
                self.stdout.write(f'Created system config: {key}')
    
    def create_college(self):
        """Create a sample college"""
        college, created = College.objects.get_or_create(
            code='TECH001',
            defaults={
                'name': 'Technology Institute of Excellence',
                'address': '123 Tech Street, Silicon Valley',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'country': 'India',
                'pincode': '560001',
                'phone': '+91-80-12345678',
                'email': 'info@techie.edu.in',
                'website': 'https://techie.edu.in',
                'established_year': 1985,
            }
        )
        if created:
            self.stdout.write(f'Created college: {college.name}')
        return college
    
    def create_departments(self, college):
        """Create sample departments"""
        dept_data = [
            ('Computer Science & Engineering', 'CSE'),
            ('Information Technology', 'IT'),
            ('Electronics & Communication', 'ECE'),
            ('Mechanical Engineering', 'ME'),
            ('Civil Engineering', 'CE'),
        ]
        
        departments = []
        for name, code in dept_data:
            dept, created = Department.objects.get_or_create(
                college=college,
                code=code,
                defaults={
                    'name': name,
                    'description': f'Department of {name}',
                }
            )
            if created:
                self.stdout.write(f'Created department: {name}')
            departments.append(dept)
        
        return departments
    
    def create_companies(self):
        """Create sample companies"""
        company_data = [
            ('TechCorp Solutions', 'mnc', 'software'),
            ('InnovateLabs', 'startup', 'software'),
            ('DataDriven Inc', 'product', 'analytics'),
            ('CloudWorks', 'service', 'cloud'),
            ('AI Innovations', 'startup', 'ai'),
        ]
        
        companies = []
        for name, company_type, industry in company_data:
            company, created = Company.objects.get_or_create(
                name=name,
                defaults={
                    'description': f'Leading {industry} company',
                    'company_type': company_type,
                    'industry': industry,
                    'headquarters': 'Bangalore, India',
                    'employee_count': random.randint(50, 5000),
                    'founded_year': random.randint(1990, 2020),
                }
            )
            if created:
                self.stdout.write(f'Created company: {name}')
            companies.append(company)
        
        return companies
    
    def create_users(self):
        """Create sample users"""
        users = []
        
        # Create super admin
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@campusconnect.com',
                password='admin123',
                user_type='super_admin',
                first_name='Super',
                last_name='Admin'
            )
            users.append(admin)
            self.stdout.write('Created super admin user')
        
        # Create TPO
        if not User.objects.filter(username='tpo').exists():
            tpo = User.objects.create_user(
                username='tpo',
                email='tpo@techie.edu.in',
                password='tpo123',
                user_type='tpo',
                first_name='Training',
                last_name='Officer'
            )
            users.append(tpo)
            self.stdout.write('Created TPO user')
        
        # Create sample students
        student_data = [
            ('john_doe', 'John', 'Doe', 'john@student.com'),
            ('jane_smith', 'Jane', 'Smith', 'jane@student.com'),
            ('raj_patel', 'Raj', 'Patel', 'raj@student.com'),
            ('priya_sharma', 'Priya', 'Sharma', 'priya@student.com'),
            ('alex_johnson', 'Alex', 'Johnson', 'alex@student.com'),
        ]
        
        for username, first_name, last_name, email in student_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='student123',
                    user_type='student',
                    first_name=first_name,
                    last_name=last_name
                )
                users.append(user)
                self.stdout.write(f'Created student user: {username}')
        
        return users
    
    def create_student_profiles(self, users, college, departments):
        """Create student profiles"""
        students = []
        student_users = [u for u in users if u.user_type == 'student']
        
        for i, user in enumerate(student_users):
            if not hasattr(user, 'student_profile'):
                profile = StudentProfile.objects.create(
                    user=user,
                    college=college,
                    department=random.choice(departments),
                    student_id=f'STU{2024}{str(i+1).zfill(3)}',
                    roll_number=f'21{str(i+1).zfill(3)}',
                    date_of_birth=date(2000 + i, random.randint(1, 12), random.randint(1, 28)),
                    gender=random.choice(['M', 'F']),
                    admission_year=2021,
                    graduation_year=2025,
                    current_semester=7,
                    cgpa=round(random.uniform(6.0, 9.5), 2),
                    percentage=round(random.uniform(60.0, 95.0), 2),
                    tenth_board='CBSE',
                    tenth_percentage=round(random.uniform(70.0, 95.0), 2),
                    tenth_year=2019,
                    twelfth_board='CBSE',
                    twelfth_percentage=round(random.uniform(65.0, 92.0), 2),
                    twelfth_year=2021,
                    placement_ready=True,
                )
                students.append(profile)
                self.stdout.write(f'Created student profile: {user.username}')
        
        return students
    
    def create_jobs(self, companies, college, departments, users):
        """Create sample jobs"""
        jobs = []
        tpo_user = next((u for u in users if u.user_type == 'tpo'), users[0])
        
        job_data = [
            ('Software Developer', 'full_time', 'Bangalore', 300000, 600000),
            ('Data Analyst', 'full_time', 'Hyderabad', 250000, 450000),
            ('Frontend Developer', 'full_time', 'Pune', 280000, 520000),
            ('Backend Engineer', 'full_time', 'Chennai', 320000, 580000),
            ('DevOps Engineer', 'full_time', 'Mumbai', 350000, 650000),
        ]
        
        for i, (title, job_type, location, sal_min, sal_max) in enumerate(job_data):
            job = Job.objects.create(
                company=companies[i % len(companies)],
                college=college,
                title=title,
                description=f'Exciting opportunity for {title} role with growth prospects.',
                job_type=job_type,
                location=location,
                salary_min=sal_min,
                salary_max=sal_max,
                min_cgpa=6.0,
                min_percentage=60.0,
                required_skills='Programming, Problem Solving, Communication',
                application_deadline=timezone.now() + timedelta(days=30),
                interview_date=timezone.now().date() + timedelta(days=45),
                joining_date=timezone.now().date() + timedelta(days=90),
                status='published',
                posted_by=tpo_user,
            )
            # Add eligible departments
            job.eligible_departments.add(*departments[:3])  # Add first 3 departments
            jobs.append(job)
            self.stdout.write(f'Created job: {title}')
        
        return jobs
    
    def create_applications(self, jobs, students):
        """Create sample applications"""
        applications = []
        
        for job in jobs:
            # Create 2-3 applications per job
            selected_students = random.sample(students, min(3, len(students)))
            
            for student in selected_students:
                application = Application.objects.create(
                    job=job,
                    student=student,
                    status=random.choice(['submitted', 'screening', 'shortlisted']),
                    cover_letter=f'I am very interested in the {job.title} position at {job.company.name}.',
                )
                applications.append(application)
                self.stdout.write(f'Created application: {student.user.username} -> {job.title}')
        
        return applications
