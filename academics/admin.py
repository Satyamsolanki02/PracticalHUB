
from django.contrib import admin
from .models import Branch, Semester, Subject


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("branch", "number")
    list_filter = ("branch", "number")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "semester")
    list_filter = ("semester",)
    search_fields = ("name", "code")
