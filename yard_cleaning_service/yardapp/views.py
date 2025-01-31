from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate, login
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from .models import Service, Order, ServiceRequest
from django.contrib import messages
from .forms import CustomUserCreationForm, EmailLoginForm, ServiceRequestForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
import os
from .models import UserProfile

# Create your views here.

def home(request):
    media_path = os.path.join(settings.MEDIA_ROOT, 'services_images')
    image_files = [f"media/services_images/{img}" for img in os.listdir(media_path) if img.endswith(('.jpg', '.jpeg', '.png', '.gif', '.jfif'))]

    return render(request, 'yardapp/home.html', {'images': image_files})

# register view

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'yardapp/register.html', {'form': form})

        
# login view
def login_view(request):
    if request.method == 'POST':
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Replace with the desired redirect URL
            else:
                form.add_error(None, 'Invalid email or password')
    else:
        form = EmailLoginForm()

    return render(request, 'yardapp/login.html', {'form': form})

# services view

def services_view(request):
    services = Service.objects.all() # get all services from the database
    return render(request, 'yardapp/services.html', {'services': services})

@login_required
def place_order(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    
    request.session['service_id'] = service.id

    return redirect('service_request')  # Redirect to the service request page

@login_required
def profile(request):
    orders = ServiceRequest.objects.filter(user=request.user)  # Fetch orders for the logged-in user
    
    pending_requests = ServiceRequest.objects.filter(user=request.user, status='Pending') # Fetch pending requests for the logged-in user

   # accepted_requests = ServiceRequest.objects.filter(user=request.user, status='Accepted') # Fetch accepted requests for the logged-in user

    context = {
        'requests': orders,
        'pending_requests': pending_requests,
    }
    return render(request, 'yardapp/profile.html', context)

# logout view
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

@login_required
# service request view
def service_request(request):
    selected_service_id = request.session.get('service_id')

    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            # fetch the user's address from their profile
            address = user_profile.address
            # Save the service request but don't finalize yet
            service_request = ServiceRequest(
                user=request.user,
                date=form.cleaned_data['date'],
                address=address,  # Use the user's address
                special_instructions=form.cleaned_data['special_instructions']
            )
            service_request.save()
            service_request.services.set(form.cleaned_data['services'])
            
            # Store the service request ID in session to pass to the confirmation page
            request.session['service_request_id'] = service_request.id
            print("Service request ID set in session:", request.session.get('service_request_id'))
            # Redirect to confirmation page
            print("Redirecting to confirmation page")  # Debug statement
            return redirect('service_request_confirmation')  # Redirect to the confirmation page if the form is valid
        else:
            print("Form is not valid")  # Debug statement
            print(form.errors)  # Print form errors for debugging

    else:
        selected_service_id = request.session.get('service_id')
        # Prefill the form with the selected service, if any
        initial_data = {'services': [selected_service_id]} if selected_service_id else {}
        form = ServiceRequestForm(initial=initial_data)

    return render(request, 'yardapp/service_request.html', {'form': form}) # render the service request form if the form is not valid

# 
@login_required
def service_request_confirmation(request):
    service_request_id = request.session.get('service_request_id')
    if not service_request_id:
        return redirect('service_request', service_id =1)  # Redirect if no service request in session

    # Retrieve the ServiceRequest instance
    service_request = get_object_or_404(ServiceRequest, id=service_request_id)

    

    # Calculate total cost of the selected services
    total_cost = sum(service.price for service in service_request.services.all())

# Send confirmation email to the user
    if request.method == 'POST':
        if 'confirm_request' in request.POST:
            # Send confirmation email to the user
            send_mail(
                'Service Request Confirmation',
                f"""Hello {service_request.user.first_name},

Thank you for your service request! Below are the details:

- Services: {', '.join(service.service_name for service in service_request.services.all())}

- Address: {service_request.address}

- Date: {service_request.date}

- Total Cost: R{total_cost}

Your request is currently {service_request.status}. We will notify you once it has been accepted or rejected.

We will contact you soon.

Best regards,  
The Yard Cleaning Service Team
""",
                settings.DEFAULT_FROM_EMAIL,
                [service_request.user.email],
                fail_silently=False,
            )

            # Notify admin about the new request
            send_mail(
                'New Service Request Received',
                f"""Admin,

A new service request has been submitted:

 User: {service_request.user.first_name} {service_request.user.last_name}

 Services: {', '.join(service.service_name for service in service_request.services.all())}

 Address: {service_request.address}

 Date: {service_request.date}

 Total Cost: R{total_cost}

The request is currently {service_request.status}. Kindly Accept or Reject the request.

Please review and follow up.

Regards,
Yard Cleaning Service System
                """,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=False,
            )

            # If the request is accepted, send an additional email to the user
            if service_request.status == 'Accepted':
                send_mail(
                    'Service Request Accepted',
                    f"""Hello {service_request.user.first_name},

Your service request has been {service_request.status}! Here are the details:

- Services: {', '.join(service.service_name for service in service_request.services.all())}

- Address: {service_request.address}

- Date: {service_request.date}

- Status: {service_request.status}

- Total Cost: ${total_cost}

Thank you for choosing us! We look forward to assisting you.

Best regards,
The Yard Cleaning Service Team
""",
                    settings.DEFAULT_FROM_EMAIL,
                    [service_request.user.email],
                    fail_silently=False,
                )

            # Redirect to a success page
            return redirect('service_request_success')

    return render(request, 'yardapp/service_request_confirmation.html', {
        'service_request': service_request,
        'total_cost': total_cost,
    })

# service request success view
@login_required
def service_request_success(request):
    return render(request, 'yardapp/service_request_success.html')