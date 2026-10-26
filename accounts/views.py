
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from academics.models import Branch, Semester, Subject
from practicals.models import PracticalPDF, Practical


def admin_required(view_func):
    return user_passes_test(
        lambda user: user.is_authenticated and user.is_superuser,
        login_url="/admin-login/",
    )(view_func)


# FACULTY LOGIN
def faculty_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if (
            user is not None
            and user.is_active
            and user.is_staff
            and not user.is_superuser
        ):
            login(request, user)
            return redirect("faculty_upload")

        messages.error(
            request,
            "Faculty username/password incorrect hai ya faculty access nahi hai.",
        )

    return render(request, "accounts/faculty_login.html")


# ADMIN LOGIN
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if (
            user is not None
            and user.is_active
            and user.is_superuser
        ):
            login(request, user)
            return redirect("admin_dashboard")

        messages.error(
            request,
            "Invalid admin username or password.",
        )

    return render(request, "accounts/admin_login.html")



# ADMIN DASHBOARD: FACULTY, BRANCHES, SEMESTERS, SUBJECTS
@admin_required
def admin_dashboard(request):
    User = get_user_model()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add":
            username = request.POST.get("username", "").strip()
            email = request.POST.get("email", "").strip()
            password = request.POST.get("password", "")

            if not username or not password:
                messages.error(
                    request,
                    "Username aur password required hain.",
                )

            elif User.objects.filter(username=username).exists():
                messages.error(
                    request,
                    "Ye username pehle se registered hai.",
                )

            else:
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_staff=True,
                    is_superuser=False,
                )

                messages.success(
                    request,
                    "Faculty account successfully created.",
                )

        elif action == "delete":
            faculty_id = request.POST.get("faculty_id")

            faculty = get_object_or_404(
                User,
                id=faculty_id,
                is_staff=True,
                is_superuser=False,
            )

            faculty.delete()

            messages.success(
                request,
                "Faculty account permanently deleted.",
            )

        return redirect("admin_dashboard")

    faculty_list = User.objects.filter(
        is_staff=True,
        is_superuser=False,
    ).order_by("username")

    context = {
        "faculty_count": faculty_list.count(),
        "faculty_list": faculty_list,
        "branch_count": Branch.objects.count(),
        "semester_count": Semester.objects.count(),
        "subject_count": Subject.objects.count(),
    }

    return render(
        request,
        "accounts/admin_dashboard.html",
        context,
    )


# LOGOUT
def faculty_logout(request):
    logout(request)
    return redirect("home")
