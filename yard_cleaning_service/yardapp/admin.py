from django.contrib import admin
from .models import UserProfile, Service, Order, OrderItem, ServiceRequest
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages
# Register your models here.

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_services', 'date', 'status')
    list_filter = ('status',)
    actions = ['accept_request', 'decline_request']

    def get_services(self, obj):
        return ", ".join([service.service_name for service in obj.services.all()])
    get_services.short_description = 'Services'

    # Custom action to accept multiple requests
    def accept_request(self, request, queryset):
        queryset.update(status='Accepted')
        for service_request in queryset:
            self.send_email(request, service_request, "Accepted")
    accept_request.short_description = 'Accept Selected Requests'

    # Custom action to decline multiple requests
    def decline_request(self, request, queryset):
        queryset.update(status='Rejected')
        for service_request in queryset:
            self.send_email(request, service_request, "Rejected")
    decline_request.short_description = 'Reject Selected Requests'

    def generate_receipt_pdf(self, service_request):
        # Generate PDF receipt for the service requested
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.drawString(100, 800, f"Service Request Receipt")
        pdf.drawString(100, 780, f"User: {service_request.user.first_name} {service_request.user.last_name}")
        pdf.drawString(100, 760, f"Services: {','.join([service.service_name for service in service_request.services.all()])}")
        pdf.drawString(100, 740, f"Address: {service_request.address}")
        pdf.drawString(100, 720, f"Date: {service_request.date}")
        pdf.drawString(100, 700, f"Status: {service_request.status}")
        pdf.drawString(100, 680, f"Total Cost: ${sum([s.cost for s in service_request.services.all()])}")
        pdf.drawString(100, 660, f"Thank you for using Yard Cleaning Service!")
        pdf.save()
        buffer.seek(0)
        return buffer
    
    def send_email(self, request, service_request, status):
        try:
            email_subject = f"Your Service Request Has Been {status}"
            email_body = f"""
            Hello {service_request.user.first_name},

            Your service request has been {status.lower()}.

            Below are your service request details:

            Details:

            - Services: {', '.join([service.service_name for service in service_request.services.all()])}
            - Address: {service_request.address}
            - Date: {service_request.date}
            - Status: {service_request.status}
            - Total Cost: ${sum([s.cost for s in service_request.services.all()])}

            Thank you for using Yard Cleaning Service!
            Best regards,
            Yard Cleaning Service Team
            """

            email = EmailMessage(
                subject=email_subject,
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[service_request.user.email],
            )
            email.send()
        except Exception as e:
            self.message_user(request, f"Failed to send an email to {service_request.user.email}. Error: {str(e)}", level=messages.ERROR)

    
    # def send_email(self, request , service_request, status):
        # Send email to the user with attached PDF receipt
        #pdf_buffer = self.generate_receipt_pdf(service_request)
        #email_subject = f"Your Service Request Has Been {status}"
        #email_body = f"Dear {service_request.user.first_name},\n\nYour service request has been {status.lower()}.\nPlease find the receipt attached.\n\nThank you!"
        #email = EmailMessage(
        #    subject = email_subject,
        #    body = email_body,
        #    from_email = settings.EMAIL_HOST_USER,
        #    to = [service_request.user.email],
        #)
        
        #email.attach(f"ServiceRequest_{status}.pdf", pdf_buffer.getvalue(), 'application/pdf')
        #email.send()
        
# Register other models
admin.site.register(UserProfile)
admin.site.register(Service)
admin.site.register(Order)
admin.site.register(OrderItem)
