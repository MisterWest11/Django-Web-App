from django.contrib.auth.models import User
from django.db import models


# Create your models here.

# Create a model for the user profile

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    province = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    
# Create a model for the services offered by the company

class Service(models.Model):
    service_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='services_images/', blank=True)


    def __str__(self):
        return self.service_name
    
# Create a model for the customer's order

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    service_date = models.DateField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f'Order by {self.id}  {self.user.first_name} {self.user.last_name} on {self.order_date}'
    
# Create a model for the order Item

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Order {self.order.id} - {self.service.service_name}'
    
# Create a model for the service request
class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    services = models.ManyToManyField(Service)  # Assuming you have a Service model
    date = models.DateField()
    address = models.CharField(max_length=100)
    special_instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        services_names = ', '.join([service.service_name for service in self.services.all()])
        return f"{self.user.first_name} {self.user.last_name} - {services_names} on {self.date} has been {self.status}"