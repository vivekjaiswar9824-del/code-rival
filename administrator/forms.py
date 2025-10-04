
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User
from django import forms
from .models import Course
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User



class DeveloperRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    DOMAIN_CHOICES = [
        ('', 'Select your Domain'),  # default placeholder
        ('Web Development', 'Web Development'),
        ('Data Science', 'Data Science'),
        ('AI/ML', 'AI/ML'),
        ('Cyber Security', 'Cyber Security'),
        # Add more as needed
    ]

    domain = forms.ChoiceField(
        choices=DOMAIN_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label='Domain'
    )

    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number', 'domain', 'skills', 'address', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Full name','id':'dev_name'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email','id': 'dev_email', 'autocomplete': 'email'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Phone number','id':'dev_phone'})
        self.fields['skills'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Skills'})
        self.fields['address'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Address', 'rows': 2,'id':'dev_address'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Create a password', 'autocomplete': 'new-password','id':'dev_password'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Roles.DEV
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


from django import forms
from .models import User  # Assuming you extended AbstractUser

class HRRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'name',
            'email',
            'phone_number',
            'address',
            'company_name',
            'password',
         
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Full name',
            'id': 'hr_name'
        })

        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'id': 'hr_email',
            'autocomplete': 'email'
        })

        self.fields['phone_number'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Phone number',
            'id': 'hr_phone'
        })

        self.fields['address'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Address',
            'id': 'hr_address',
            'rows': 2  
        })

        self.fields['company_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Company name'
        })

        

        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create password',
            'id': 'hr_password',
            'autocomplete': 'new-password'
        })

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email.endswith(('.com', '.org', '.net')):
            raise forms.ValidationError("Use a valid company domain.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Roles.HR
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your email',
             'autocomplete': 'email'

        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'id':'id_password'
        })





class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'domain', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter course title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter course description',
                'rows': 4
            }),
            'domain': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }





from django import forms
from .models import Certification

class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['user', 'course', 'level', 'score', 'status']
        widgets = {
            'level': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'score': forms.NumberInput(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
        }




# administrator/forms.py

from django import forms
from .models import Question

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'stage': forms.Select(attrs={'class': 'form-control'}),
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'option_a': forms.TextInput(attrs={'class': 'form-control'}),
            'option_b': forms.TextInput(attrs={'class': 'form-control'}),
            'option_c': forms.TextInput(attrs={'class': 'form-control'}),
            'option_d': forms.TextInput(attrs={'class': 'form-control'}),
            'correct_answer': forms.Select(attrs={'class': 'form-control'}),
        }


# Removed ForgotPasswordForm - replaced by Django built-in password reset
identifier = forms.CharField(max_length=100, required=True, label='Email or Phone Number',
                               widget=forms.TextInput(attrs={
                                   'class': 'form-control',
                                   'placeholder': 'Enter your email or phone number'
                               }))


# Removed OTPVerificationForm - replaced by Django built-in password reset
otp = forms.CharField(max_length=6, required=True, label='OTP',
                         widget=forms.TextInput(attrs={
                             'class': 'form-control',
                             'placeholder': 'Enter the 6-digit OTP',
                             'pattern': '[0-9]{6}',
                             'title': 'OTP must be 6 digits'
                         }))


# Removed ResetPasswordForm - replaced by Django built-in password reset
new_password = forms.CharField(max_length=128, required=True, label='New Password',
                                 widget=forms.PasswordInput(attrs={
                                     'class': 'form-control',
                                     'placeholder': 'Enter new password',
                                     'autocomplete': 'new-password'
                                 }))
confirm_password = forms.CharField(max_length=128, required=True, label='Confirm Password',
                                     widget=forms.PasswordInput(attrs={
                                         'class': 'form-control',
                                         'placeholder': 'Confirm new password',
                                         'autocomplete': 'new-password'
                                     }))
    
def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        
        return cleaned_data
