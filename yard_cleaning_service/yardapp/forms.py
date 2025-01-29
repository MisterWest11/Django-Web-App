from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Service, ServiceRequest

# Custom Login Form
class EmailLoginForm(forms.Form):
    email = forms.EmailField(required=True, label="Email")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Password")



# Custom User Registration Form
class CustomUserCreationForm(forms.ModelForm):
    # Fields from the User model
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput, required=True)

    # Fields from the UserProfile model
    phone = forms.CharField(max_length=20, required=True)
    address = forms.CharField(max_length=100, required=True)
    city = forms.CharField(max_length=50, required=True)
    province = forms.CharField(max_length=50, required=True)
    zip_code = forms.CharField(max_length=10, required=True)
    profile_pic = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

        
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists!")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                address=self.cleaned_data['address'],
                city=self.cleaned_data['city'],
                province=self.cleaned_data['province'],
                zip_code=self.cleaned_data['zip_code'],
                profile_pic=self.cleaned_data.get('profile_pic'),
            )
        return user
    
# Custom Service Request Form
class ServiceRequestForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=True
    )

    class Meta:
        model = ServiceRequest
        fields = ['services', 'date', 'special_instructions']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'special_instructions': forms.TextInput(attrs={'rows': 3}),
        }