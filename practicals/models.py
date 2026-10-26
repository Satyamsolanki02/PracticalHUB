
from django.db import models
from academics.models import Subject
import uuid


def practical_pdf_path(instance, filename):
    return f"practicals/{instance.subject.id}/{filename}"


class PracticalPDF(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="practical_pdfs"
    )
    title = models.CharField(max_length=200)
    pdf_file = models.FileField(upload_to=practical_pdf_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject.name} - {self.title}"


class Practical(models.Model):
    pdf = models.ForeignKey(
        PracticalPDF,
        on_delete=models.CASCADE,
        related_name="practicals"
    )
    name = models.CharField(max_length=200)
    start_page = models.PositiveIntegerField()
    qr_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    class Meta:
        ordering = ["start_page"]

    def __str__(self):
        return self.name
