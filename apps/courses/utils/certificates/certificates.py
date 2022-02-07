import os
import hashlib
from io import BytesIO
from random import randint

import pdfkit
import qrcode
from django.core.files import File
from django.core.files.base import ContentFile

from ....accounts.models import User
from ....courses.models import CourseCertificate, Course, CertificatedCourse


def get_modified_html(html: str, text_to_split: str, value_to_insert: str):
    """text_to_split: text which will be popped. Value_to_insert will be added to that place"""
    html_parts = html.split(text_to_split)
    html_parts[1] = f'{value_to_insert} {html_parts[1]}'
    return ''.join(html_parts)


def create_certificate_pdf(full_name: str, image_path: str, award_date, course_name: str,
                           certificate_path: str = 'apps/courses/utils/certificates/certificate.html'):
    """Get the html code, edit it, save the modified version in a file.
    Generate a pdf from the new html and delete the html file
    """
    with open(certificate_path, 'r') as certificate_file:
        certificate_html = certificate_file.read().replace('\n', '')

    certificate_html = get_modified_html(certificate_html, 'certname', full_name)
    certificate_html = get_modified_html(certificate_html, 'qrcode', f'<img src="/code/{image_path}" />')
    certificate_html = get_modified_html(certificate_html, 'awarddate', award_date.strftime("%m/%d/%Y"))
    certificate_html = get_modified_html(certificate_html, 'coursename', course_name)

    new_certificate_path = f'apps/courses/utils/certificates/certificate{randint(0, 999999)}.html'
    with open(new_certificate_path, 'w') as html:
        html.write(certificate_html)

    certificate_pdf = pdfkit.from_file(new_certificate_path, False)
    os.remove(new_certificate_path)
    return certificate_pdf


def create_bytes_certificate_qrcode(qrcode_data: str):
    certificate_qr = qrcode.make(qrcode_data)
    blob = BytesIO()
    certificate_qr.save(blob, 'png')
    return blob


def create_certificate(user: User, domain: str, course: Course = None, certificated_course: CertificatedCourse = None):
    assert course or certificated_course, "Course or certificated course must be defined"
    if course:
        certificate = CourseCertificate.objects.create(user=user, course=course)
    else:
        certificate = CourseCertificate.objects.create(user=user, certificated_course=certificated_course)

    certificate_hash = f'{user.id}{randint(0, 99999)}-borow'
    certificate.hash = hashlib.md5(bytes(certificate_hash, encoding='utf8')).hexdigest()

    certificate_qr = create_bytes_certificate_qrcode(get_qr_data(certificate.hash, domain))
    certificate.qr.save(f'{user.phone}.png', File(certificate_qr))

    certificate_pdf = create_certificate_pdf(
        full_name=user.profile.get_full_name(), image_path=certificate.qr.url,
        award_date=certificate.created_at, course_name=certificate.certificated_object.name
    )
    certificate.pdf.save(f'{randint(0, 3434)}{certificate.certificated_object.name}.pdf',
                         ContentFile(certificate_pdf))

    certificate.save()
    return certificate


def get_qr_data(certificate_hash: str, domain: str) -> str:
    if '/' == domain[-1]:
        domain = domain[:-1]
    return f'{domain}/certificates-verify/{certificate_hash}/'
