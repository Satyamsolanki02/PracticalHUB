
from django import forms
from academics.models import Branch, Semester, Subject
from practicals.models import PracticalPDF


class PracticalUploadForm(forms.ModelForm):
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        empty_label="Select Branch"
    )

    semester = forms.ModelChoiceField(
        queryset=Semester.objects.none(),
        empty_label="Select Semester"
    )

    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),
        empty_label="Select Subject"
    )

    class Meta:
        model = PracticalPDF
        fields = ["title", "pdf_file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        data = self.data if self.is_bound else {}

        if data.get("branch"):
            try:
                self.fields["semester"].queryset = Semester.objects.filter(
                    branch_id=int(data["branch"])
                )
            except (ValueError, TypeError):
                pass

        if data.get("semester"):
            try:
                self.fields["subject"].queryset = Subject.objects.filter(
                    semester_id=int(data["semester"])
                )
            except (ValueError, TypeError):
                pass

    def clean(self):
        cleaned_data = super().clean()
        branch = cleaned_data.get("branch")
        semester = cleaned_data.get("semester")
        subject = cleaned_data.get("subject")

        if branch and semester and semester.branch_id != branch.id:
            self.add_error("semester", "Please select a semester from this branch.")

        if semester and subject and subject.semester_id != semester.id:
            self.add_error("subject", "Please select a subject from this semester.")

        return cleaned_data

    def save(self, commit=True):
        pdf = super().save(commit=False)
        pdf.subject = self.cleaned_data["subject"]

        if commit:
            pdf.save()

        return pdf
class PracticalReviewForm(forms.Form):
    name = forms.CharField(
        max_length=200,
        label="Practical Name"
    )
    start_page = forms.IntegerField(
        min_value=1,
        label="Starting Page"
    )