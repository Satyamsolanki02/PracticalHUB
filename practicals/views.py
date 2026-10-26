from io import BytesIO
import qrcode

from django.contrib import messages
from django.db import transaction
from django.forms import formset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from academics.models import Branch, Semester, Subject
from practicals.models import PracticalPDF, Practical
from practicals.forms import PracticalUploadForm, PracticalReviewForm
from practicals.utils import detect_practicals

from django.contrib.auth.decorators import login_required, user_passes_test

def home(request):
    return render(request, "home.html", {
        "branches": Branch.objects.all()
    })


def about(request):
    return render(request, "about.html")


def branch_detail(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    semesters = Semester.objects.filter(branch=branch)
    return render(request, "branch_detail.html", {
        "branch": branch,
        "semesters": semesters,
    })


def semester_detail(request, semester_id):
    semester = get_object_or_404(Semester, id=semester_id)
    subjects = Subject.objects.filter(semester=semester)
    return render(request, "semester_detail.html", {
        "semester": semester,
        "subjects": subjects,
    })


def subject_detail(request, subject_id):
    import os

    subject = get_object_or_404(Subject, id=subject_id)

    all_pdfs = subject.practical_pdfs.all()

    practical_pdfs = [
        pdf for pdf in all_pdfs
        if pdf.pdf_file and os.path.isfile(pdf.pdf_file.path)
    ]

    return render(request, "subject_detail.html", {
        "subject": subject,
        "practical_pdfs": practical_pdfs,
    })

def practical_qr(request, token):
    practical = get_object_or_404(Practical, qr_token=token)

    url = request.build_absolute_uri(
        reverse("practical_detail", kwargs={"token": str(practical.qr_token)})
    )

    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    return HttpResponse(buffer.getvalue(), content_type="image/png")


def practical_detail(request, token):
    practical = get_object_or_404(Practical, qr_token=token)

    return render(request, "practical_detail.html", {
        "practical": practical,
        "pdf_url": (
            practical.pdf.pdf_file.url
            + "#page="
            + str(practical.start_page)
        ),
        "page_number": practical.start_page,
    })
    
@login_required(login_url="/faculty/login/")
@user_passes_test(
    lambda user: user.is_staff and not user.is_superuser,
    login_url="/faculty/login/",
)

def faculty_upload(request):
    detected_practicals = []
    uploaded_pdf = None
    review_error = None
    form = PracticalUploadForm()

    saved_pdf_id = request.GET.get("pdf_id")

    if request.method == "GET" and saved_pdf_id:
        uploaded_pdf = get_object_or_404(PracticalPDF, pk=saved_pdf_id)
        detected_practicals = [
            {
                "id": p.id,
                "name": p.name,
                "start_page": p.start_page,
                "qr_token": p.qr_token,
            }
            for p in uploaded_pdf.practicals.all()
        ]

    if request.method == "POST":
        if request.POST.get("action") == "save_practicals":
            uploaded_pdf = get_object_or_404(
                PracticalPDF, pk=request.POST.get("pdf_id")
            )

            ReviewFormSet = formset_factory(
                PracticalReviewForm, extra=0
            )
            formset = ReviewFormSet(request.POST)

            if formset.is_valid() and formset.total_form_count() > 0:
                import fitz

                with fitz.open(uploaded_pdf.pdf_file.path) as document:
                    total_pages = len(document)

                valid_items = []
                seen = set()

                for item in formset.cleaned_data:
                    if not item:
                        continue

                    name = item["name"].strip()
                    page = item["start_page"]

                    if not name:
                        review_error = "Practical name cannot be empty."
                        break

                    if page > total_pages:
                        review_error = (
                            f'"{name}" ka page {page} hai, '
                            f'lekin PDF mein sirf {total_pages} pages hain.'
                        )
                        break

                    key = (name.casefold(), page)
                    if key not in seen:
                        seen.add(key)
                        valid_items.append((name, page))

                if not review_error:
                    with transaction.atomic():
                        for name, page in valid_items:
                            Practical.objects.get_or_create(
                                pdf=uploaded_pdf,
                                name=name,
                                start_page=page,
                            )

                    messages.success(
                        request,
                        "Practicals saved! QR codes are ready."
                    )
                    return redirect(
                        f'{reverse("faculty_upload")}?pdf_id={uploaded_pdf.id}'
                    )

            else:
                review_error = (
                    "Form valid nahi hai. Names aur page numbers check karo."
                )

            detected_practicals = [
                {
                    "name": item.get("name", ""),
                    "start_page": item.get("start_page", 1),
                }
                for item in getattr(formset, "cleaned_data", [])
                if item
            ]

        else:
            form = PracticalUploadForm(request.POST, request.FILES)

            if form.is_valid():
                uploaded_pdf = form.save()

                try:
                    detected_practicals = detect_practicals(
                        uploaded_pdf.pdf_file.path
                    )
                except Exception as error:
                    review_error = f"PDF scan nahi ho paya: {error}"

                if detected_practicals:
                    messages.info(
                        request,
                        "Detected practicals ko verify karke save karo."
                    )
            else:
                return render(request, "faculty_upload.html", {
                    "form": form,
                    "detected_practicals": [],
                    "uploaded_pdf": None,
                    "review_error": None,
                })

    return render(request, "faculty_upload.html", {
        "form": form,
        "detected_practicals": detected_practicals,
        "uploaded_pdf": uploaded_pdf,
        "review_error": review_error,
    })


def get_semesters(request):
    branch_id = request.GET.get("branch_id")
    semesters = Semester.objects.filter(
        branch_id=branch_id
    ).order_by("number")

    return JsonResponse({
        "semesters": [
            {"id": s.id, "name": f"Semester {s.number}"}
            for s in semesters
        ]
    })


def get_subjects(request):
    semester_id = request.GET.get("semester_id")
    subjects = Subject.objects.filter(
        semester_id=semester_id
    ).order_by("name")

    return JsonResponse({
        "subjects": [
            {"id": s.id, "name": s.name}
            for s in subjects
        ]
    })
