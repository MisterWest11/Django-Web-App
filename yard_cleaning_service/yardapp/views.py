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

# Create your views here.

def home(request):
    return render(request, 'yardapp/home.html')

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
    if request.method == 'POST':
        # Placeholder for saving the order logic
        messages.success(request, f"You've successfully ordered: {service.service_name}!")
        return redirect('services')
    return redirect('services')

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user)  # Fetch orders for the logged-in user
    return render(request, 'yardapp/profile.html', {'orders': orders})

# logout view
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

@login_required
# service request view
def service_request(request, service_id):
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            # Save the service request but don't finalize yet
            service_request = ServiceRequest(
                user=request.user,
                date=form.cleaned_data['date'],
                time=form.cleaned_data['time'],
                address=form.cleaned_data['address'],
                special_instructions=form.cleaned_data['special_instructions']
            )
            service_request.save()
            service_request.services.set(form.cleaned_data['services'])
            
            # Store the service request ID in session to pass to the confirmation page
            request.session['service_request_id'] = service_request.id
            
            # Redirect to confirmation page
            return redirect('service_request_confirmation')

    else:
        form = ServiceRequestForm()

    return render(request, 'yardapp/service_request.html', {'form': form})

# 
@login_required
def service_request_confirmation(request):
    service_request_id = request.session.get('service_request_id')
    if not service_request_id:
        return redirect('service_request')  # Redirect if no service request in session

    # Retrieve the ServiceRequest instance
    service_request = get_object_or_404(ServiceRequest, id=service_request_id)

    # Calculate total cost of the selected services
    total_cost = sum(service.cost for service in service_request.services.all())

    if request.method == 'POST':
        if 'confirm_request' in request.POST:
            # Send confirmation email to the user
            send_mail(
                'Service Request Confirmation',
                f"""Hello {service_request.user.first_name},

Thank you for your request! Here are the details:
- Services: {', '.join(service.name for service in service_request.services.all())}
- Address: {service_request.address}
- Date: {service_request.date}
- Time: {service_request.time}
- Total Cost: ${total_cost}

We will contact you shortly.

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
- User: {service_request.user.first_name} {service_request.user.last_name}
- Services: {', '.join(service.name for service in service_request.services.all())}
- Total Cost: ${total_cost}

Please review and follow up.

Regards,
Yard Cleaning Service System
                """,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=False,
            )

            # Redirect to a success page
            return redirect('service_request_success')

    return render(request, 'yardapp/service_request_confirmation.html', {
        'service_request': service_request,
        'total_cost': total_cost,
    })
# 