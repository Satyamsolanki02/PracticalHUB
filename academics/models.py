from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.code


class Semester(models.Model):
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="semesters"
    )
    number = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ("branch", "number")
        ordering = ["number"]

    def __str__(self):
        return f"{self.branch.code} - Semester {self.number}"


class Subject(models.Model):
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="subjects"
    )
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name