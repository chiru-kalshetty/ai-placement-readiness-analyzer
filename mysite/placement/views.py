from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Student
import csv


# 📝 SIGNUP VIEW
def signup(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password or not confirm_password:
            messages.error(request, "All fields are required.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, "Account created successfully! Welcome to Placement Predictor.")
            return redirect('dashboard')

    return render(request, 'placement/signup.html')


# 🏠 LANDING PAGE VIEW
def landing_page(request):
    return render(request, 'placement/form.html')


# 🔥 FORM VIEW
@login_required(login_url='login')
def student_form(request):
    result = None
    score = None
    level = None
    suggestions = []
    resume_message = None
    errors = []

    if request.method == "POST":
        # Get form data
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        branch = request.POST.get('branch', '')
        technical_skills = request.POST.get('technical_skills', '').strip()
        soft_skills = request.POST.get('soft_skills', '').strip()
        leadership = request.POST.get('leadership', '').strip()

        # Validate required fields
        if not name:
            errors.append("Name is required")
        if not email:
            errors.append("Email is required")
        elif '@' not in email or '.' not in email:
            errors.append("Please enter a valid email address")
        if not branch:
            errors.append("Please select a branch")
        if not technical_skills:
            errors.append("Technical skills are required")

        # Validate numeric fields
        try:
            cgpa = float(request.POST.get('cgpa', 0))
            if cgpa < 0 or cgpa > 10:
                errors.append("CGPA must be between 0 and 10")
        except ValueError:
            errors.append("Please enter a valid CGPA")

        try:
            projects = int(request.POST.get('projects', 0))
            if projects < 0:
                errors.append("Projects cannot be negative")
        except ValueError:
            errors.append("Please enter a valid number for projects")

        try:
            internships = int(request.POST.get('internships', 0))
            if internships < 0:
                errors.append("Internships cannot be negative")
        except ValueError:
            errors.append("Please enter a valid number for internships")

        try:
            certifications = int(request.POST.get('certifications', 0))
            if certifications < 0:
                errors.append("Certifications cannot be negative")
        except ValueError:
            errors.append("Please enter a valid number for certifications")

        try:
            aptitude = int(request.POST.get('aptitude', 0))
            if aptitude < 0 or aptitude > 10:
                errors.append("Aptitude score must be between 0 and 10")
        except ValueError:
            errors.append("Please enter a valid aptitude score (0-10)")

        try:
            communication = int(request.POST.get('communication', 0))
            if communication < 0 or communication > 10:
                errors.append("Communication score must be between 0 and 10")
        except ValueError:
            errors.append("Please enter a valid communication score (0-10)")

        # If no errors, proceed with saving
        if not errors:
            Student.objects.create(
                user=request.user,
                name=name,
                email=email,
                branch=branch,
                cgpa=cgpa,
                technical_skills=technical_skills,
                soft_skills=soft_skills,
                projects=projects,
                internships=internships,
                certifications=certifications,
                aptitude=aptitude,
                communication=communication,
                leadership=leadership
            )

            # SCORE
            score = (cgpa * 10) + (projects * 8) + (internships * 12) + (certifications * 5) + (aptitude * 5) + (communication * 5)
            score = min(score, 100)

            # RESUME HANDLING
            resume_message = None
            if 'resume' in request.FILES:
                resume_file = request.FILES['resume']
                # Basic check: just filename
                if resume_file.name:
                    score += 5  # slight increase
                    score = min(score, 100)
                    resume_message = "Resume uploaded successfully"

            # RESULT
            if score >= 85:
                result = "Highly Placement Ready ✅"
                level = "🏆 Elite"
            elif score >= 70:
                result = "Placement Ready ✅"
                level = "🥇 Skilled"
            elif score >= 50:
                result = "Needs Improvement ⚠"
                level = "🥈 Beginner"
            else:
                result = "Not Ready ❌"
                level = "❌ Needs Work"

            # AI Suggestions
            if cgpa < 7:
                suggestions.append("📚 Focus on improving your academics - aim for higher CGPA through consistent study.")
            if internships == 0:
                suggestions.append("💼 Gain practical experience by doing internships in your field.")
            if projects < 2:
                suggestions.append("🚀 Build more projects to showcase your skills on GitHub/portfolio.")
            if communication < 5:
                suggestions.append("🗣️ Work on communication skills - join public speaking clubs or take courses.")
            if aptitude < 5:
                suggestions.append("🧠 Practice aptitude tests regularly to improve logical reasoning.")

            messages.success(request, "Analysis Completed! Your placement score has been calculated successfully.")
            return redirect('analyze')

    if errors:
        for err in errors:
            messages.error(request, err)

    return render(request, 'placement/analyze.html', {
        'result': result,
        'score': score,
        'level': level,
        'suggestions': suggestions,
        'resume_message': resume_message,
        'errors': errors,
    })


# 🔐 LOGIN VIEW
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, 'placement/login.html')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful. Welcome back!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'placement/login.html')


# 🔐 LOGOUT VIEW
def user_logout(request):
    logout(request)
    return redirect('login')


# 🔥 🔐 PROTECTED DASHBOARD (FIXED)
@login_required(login_url='login')   # ✅ THIS IS THE FIX
def dashboard(request):
    all_branches = [choice[0] for choice in Student.BRANCH_CHOICES]
    # Get all students for current user initially
    students = Student.objects.filter(user=request.user)

    # Get filter parameters
    branch_filter = request.GET.get('branch', '')
    score_min = request.GET.get('score_min', '')
    score_max = request.GET.get('score_max', '')

    # Apply filters
    if branch_filter:
        students = students.filter(branch=branch_filter)

    # Filter by score range if provided
    if score_min or score_max:
        filtered_students = []
        for s in students:
            score = (s.cgpa * 10) + (s.projects * 8) + (s.internships * 12) + (s.certifications * 5) + (s.aptitude * 5) + (s.communication * 5)
            score = min(score, 100)

            min_score = float(score_min) if score_min else 0
            max_score = float(score_max) if score_max else 100

            if min_score <= score <= max_score:
                filtered_students.append(s)

        # Convert back to queryset-like object
        student_ids = [s.id for s in filtered_students]
        students = Student.objects.filter(id__in=student_ids, user=request.user)

    # Calculate statistics
    total = students.count()
    selected = students.filter(cgpa__gte=7).count()
    not_selected = total - selected

    avg_cgpa = 0
    if total > 0:
        avg_cgpa = sum([s.cgpa for s in students]) / total

    # Build leaderboard from filtered students
    leaderboard = []
    for s in students:
        score = (s.cgpa * 10) + (s.projects * 8) + (s.internships * 12) + (s.certifications * 5) + (s.aptitude * 5) + (s.communication * 5)
        score = min(score, 100)
        leaderboard.append({
            'name': s.name,
            'cgpa': s.cgpa,
            'projects': s.projects,
            'internships': s.internships,
            'score': score,
            'email': s.email,
            'branch': s.branch,
        })

    leaderboard.sort(key=lambda x: x['score'], reverse=True)

    # Calculate branch-wise statistics
    branch_stats = {}
    all_students = Student.objects.filter(user=request.user)  # Use all students for branch stats, not filtered

    for branch in all_students.values_list('branch', flat=True).distinct():
        branch_students = all_students.filter(branch=branch)
        branch_count = branch_students.count()

        # Calculate average score for this branch
        total_score = 0
        for s in branch_students:
            score = (s.cgpa * 10) + (s.projects * 8) + (s.internships * 12) + (s.certifications * 5) + (s.aptitude * 5) + (s.communication * 5)
            score = min(score, 100)
            total_score += score

        avg_score = total_score / branch_count if branch_count > 0 else 0

        branch_stats[branch] = {
            'count': branch_count,
            'avg_score': round(avg_score, 2)
        }

    # Prepare data for charts
    branch_labels = list(branch_stats.keys())
    branch_counts = [branch_stats[branch]['count'] for branch in branch_labels]
    branch_avg_scores = [branch_stats[branch]['avg_score'] for branch in branch_labels]

    return render(request, 'placement/dashboard.html', {
        'students': students,
        'total': total,
        'selected': selected,
        'not_selected': not_selected,
        'avg_cgpa': round(avg_cgpa, 2),
        'leaderboard': leaderboard,
        'all_branches': all_branches,
        'current_branch': branch_filter,
        'current_score_min': score_min,
        'current_score_max': score_max,
        'branch_labels': branch_labels,
        'branch_counts': branch_counts,
        'branch_avg_scores': branch_avg_scores,
        'branch_stats': branch_stats,
    })

# 📊 EXPORT CSV VIEW
@login_required(login_url='login')
def export_csv(request):
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="placement_report.csv"'

    # Create CSV writer
    writer = csv.writer(response)

    # Get all students for current user
    students = Student.objects.filter(user=request.user)

    # Write header row
    writer.writerow([
        'Name', 'Email', 'Branch', 'CGPA', 'Technical Skills',
        'Soft Skills', 'Projects', 'Internships', 'Certifications',
        'Aptitude Score', 'Communication Score', 'Leadership',
        'Calculated Score', 'Placement Status'
    ])

    for student in students:
        score = (student.cgpa * 10) + (student.projects * 8) + (student.internships * 12) + \
                (student.certifications * 5) + (student.aptitude * 5) + (student.communication * 5)
        score = min(score, 100)
        placement_status = "Selected" if student.cgpa >= 7 else "Not Selected"

        writer.writerow([
            student.name,
            student.email,
            student.branch,
            student.cgpa,
            student.technical_skills,
            student.soft_skills,
            student.projects,
            student.internships,
            student.certifications,
            student.aptitude,
            student.communication,
            student.leadership,
            round(score, 2),
            placement_status
        ])

    return response


@login_required(login_url='login')
def export_students_csv(request):
    return export_csv(request)

    # Write header row
    writer.writerow([
        'Name', 'Email', 'Branch', 'CGPA', 'Technical Skills',
        'Soft Skills', 'Projects', 'Internships', 'Certifications',
        'Aptitude Score', 'Communication Score', 'Leadership',
        'Calculated Score', 'Placement Status'
    ])

    # Get all students for current user
    students = Student.objects.filter(user=request.user)

    # Write data rows
    for student in students:
        # Calculate score
        score = (student.cgpa * 10) + (student.projects * 8) + (student.internships * 12) + \
                (student.certifications * 5) + (student.aptitude * 5) + (student.communication * 5)
        score = min(score, 100)

        # Determine placement status
        placement_status = "Selected" if student.cgpa >= 7 else "Not Selected"

        writer.writerow([
            student.name,
            student.email,
            student.branch,
            student.cgpa,
            student.technical_skills,
            student.soft_skills,
            student.projects,
            student.internships,
            student.certifications,
            student.aptitude,
            student.communication,
            student.leadership,
            round(score, 2),
            placement_status
        ])

    return response

# � STUDENT PROFILE PAGE
@login_required(login_url='login')
def profile(request):
    # Fetch latest student for current user
    student = Student.objects.filter(user=request.user).last()

    if not student:
        return render(request, 'placement/profile.html', {
            'no_data': True,
        })

    # Calculate score
    score = (student.cgpa * 10) + (student.projects * 8) + (student.internships * 12) + (student.certifications * 5) + (student.aptitude * 5) + (student.communication * 5)
    score = min(score, 100)
    remaining_score = 100 - score

    # Badge system
    if score >= 85:
        badge = "🏆 Elite"
    elif score >= 70:
        badge = "🥇 Skilled"
    elif score >= 50:
        badge = "🥈 Beginner"
    else:
        badge = "⚠ Needs Work"

    return render(request, 'placement/profile.html', {
        'student': student,
        'score': score,
        'remaining_score': remaining_score,
        'badge': badge,
        'no_data': False,
    })


# �📞 SUPPORT PAGE
@login_required(login_url='login')
def support(request):
    return render(request, 'placement/support.html')