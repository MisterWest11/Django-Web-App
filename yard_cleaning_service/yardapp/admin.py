from django.contrib import admin
from .models import UserProfile, Service, Order, OrderItem, ServiceRequest
# Register your models here.

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_services', 'date', 'time', 'status')
    list_filter = ('status',)
    actions = ['accept_request', 'decline_request']

    def get_services(self, obj):
        return ", ".join([service.service_name for service in obj.services.all()])
    get_services.short_description = 'Services'

    def accept_request(self, request, queryset):
        queryset.update(status='Accepted')
    accept_request.short_description = 'Accept Selected Requests'

    def decline_request(self, request, queryset):
        queryset.update(status='Declined')
    decline_request.short_description = 'Decline Selected Requests'

admin.site.register(UserProfile)
admin.site.register(Service)
admin.site.register(Order)
admin.site.register(OrderItem)


