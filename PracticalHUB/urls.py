
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from practicals import views

from accounts import views as account_views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    # Separate faculty login
    path("faculty/", include("accounts.urls")),
    path("faculty/upload/", views.faculty_upload, name="faculty_upload"),
    
    # Separate admin login and dashboard
    path("admin-login/", account_views.admin_login, name="admin_login"),
    path("admin-dashboard/", account_views.admin_dashboard, name="admin_dashboard"),
    
    path("branch/<int:branch_id>/", views.branch_detail, name="branch_detail"),
    path("semester/<int:semester_id>/", views.semester_detail, name="semester_detail"),
    path("subject/<int:subject_id>/", views.subject_detail, name="subject_detail"),

    path("qr/<uuid:token>/", views.practical_qr, name="practical_qr"),
    path("practical/<uuid:token>/", views.practical_detail, name="practical_detail"),

    path("ajax/semesters/", views.get_semesters, name="get_semesters"),
    path("ajax/subjects/", views.get_subjects, name="get_subjects"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
