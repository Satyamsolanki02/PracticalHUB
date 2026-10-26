from django.contrib import admin
from .models import PracticalPDF, Practical


class PracticalInline(admin.TabularInline):
    model = Practical
    extra = 1


@admin.register(PracticalPDF)
class PracticalPDFAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "uploaded_at")
    list_filter = ("subject",)
    inlines = [PracticalInline]


@admin.register(Practical)
class PracticalAdmin(admin.ModelAdmin):
    list_display = ("name", "pdf", "start_page")
    list_filter = ("pdf",)