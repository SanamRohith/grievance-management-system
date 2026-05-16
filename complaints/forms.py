from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from .models import Profile
from .models import Complaint
import os

class RegisterForm(forms.ModelForm):

    role = forms.ChoiceField(
        choices=[('', 'Select Role'), ('student', 'Student'), ('staff', 'Staff')],
        required=True,
        widget=forms.Select(attrs={'placeholder': 'Role'})
    )
    
    year_of_study = forms.ChoiceField(
        choices=[('', 'Select Year'), ('1', '1st Year'), ('2', '2nd Year'), ('3', '3rd Year'), ('4', '4th Year')],
        required=False,
        widget=forms.Select(attrs={'placeholder': 'Year of Study'})
    )

    department = forms.ChoiceField(
        choices=[('', 'Select Department'), ('cse', 'CSE'), ('cst', 'CST'), ('ece', 'ECE'), ('ect', 'ECT'), ('cai', 'CAI'), 
             ('aiml', 'AIML'), ('mech', 'MECH'), ('civil', 'CIVIL'), ('eee', 'EEE'), ('mba', 'MBA'), ('diploma', 'Diploma')],
        required=True,
        widget=forms.Select(attrs={'placeholder': 'Department'})
    )
    
    contact_number = forms.CharField(
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit contact number.')],
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Contact number'})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        label="Password",
        required=True,
        validators=[
            MinLengthValidator(8),
            RegexValidator(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
                           'Password must contain at least 8 characters, including uppercase, lowercase, number, and special character.')
        ]
    )

    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        label="Password confirmation",
        required=True
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs={'placeholder': 'Password'}),
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }

    # Validation for email uniqueness
    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     if User.objects.filter(email=email).exists():
    #         raise forms.ValidationError("This email address is already registered.")
    #     return email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

    # Validation for contact number uniqueness
    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number')
        if Profile.objects.filter(contact_number=contact_number).exists():
            raise forms.ValidationError("This contact number is already registered.")
        return contact_number
    
    # Ensure password and password_confirm match
    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match.")
        return password_confirm
    
    def clean_year_of_study(self):
        role = self.cleaned_data.get('role')
        year_of_study = self.cleaned_data.get('year_of_study')
        if role == 'staff' and year_of_study:
            raise forms.ValidationError("Staff members should not select a year of study.")
        return year_of_study
    
    def clean(self):
        # Fetch the cleaned data
        cleaned_data = super().clean()
        
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        role = cleaned_data.get('role')
        year_of_study = cleaned_data.get('year_of_study')

        # # Check if first_name contains only alphabetic characters
        # if first_name and not first_name.isalpha():
        #     self.add_error('first_name', 'First name should contain only alphabetic characters.')
        # elif not first_name:
        #     self.add_error('first_name', 'First name is required.')

        # # Check if last_name contains only alphabetic characters
        # if last_name and not last_name.isalpha():
        #     self.add_error('last_name', 'Last name should contain only alphabetic characters.')
        # elif not last_name:
        #     self.add_error('last_name', 'Last name is required.')

                # Check first name
        if first_name:
            if not all(char.isalpha() or char.isspace() for char in first_name):
                self.add_error('first_name', 'First name should contain only alphabetic characters')
        else:
            self.add_error('first_name', 'First name is required.')

        # Check last name
        if last_name:
            if not all(char.isalpha() or char.isspace() for char in last_name):
                self.add_error('last_name', 'Last name should contain only alphabetic characters')
        else:
            self.add_error('last_name', 'Last name is required.')

        # If role is 'student', ensure year_of_study is provided
        if role == 'student' and not year_of_study:
            self.add_error('year_of_study', 'Year of study is required for students.')

        # Return cleaned_data at the end of the method
        return cleaned_data
        
    # Save method to create User and Profile
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hash the password
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                department=self.cleaned_data['department'],
                contact_number=self.cleaned_data['contact_number'],
                year_of_study=self.cleaned_data['year_of_study'] if self.cleaned_data['role'] == 'student' else None
            )
        return user

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['subject', 'type', 'description','image', 'file']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the subject of your complaint',
                'id': 'subject'
            }),
            'type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'type'
            }, choices=[
                ('Infrastructure','Infrastructure'),
                ('Faculty','Faculty'),
                ('Women Grievance','Women Grievance'),
                ('Ragging', 'Ragging'),
                ('Hostel', 'Hostel'),
                ('Transport', 'Transport'),
                ('Canteen', 'Canteen'),
                ('Other', 'Other'),
            ]),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the description of your complaint',
                'id': 'description'
            }),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx']
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError('Unsupported file extension. Allowed extensions are: .jpg, .jpeg, .png, .pdf, .doc, .docx')
        return file

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            valid_extensions = ['.jpg', '.jpeg', '.png']
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError('Unsupported image extension. Allowed extensions are: .jpg, .jpeg, .png')
        return image


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'username': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

class ProfileForm(forms.ModelForm):
    year_of_study = forms.ChoiceField(
        choices=[('', 'Select Year'), ('1', '1st Year'), ('2', '2nd Year'), ('3', '3rd Year'), ('4', '4th Year')],
        required=False,  # Make it optional for staff
        widget=forms.Select(attrs={'placeholder': 'Year of Study'})
    )

    class Meta:
        model = Profile
        fields = ['contact_number', 'department', 'year_of_study']


from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

class CustomPasswordResetForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Current Password",
        required=True
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="New Password",
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm New Password",
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("New passwords do not match.")

        if not self.is_password_complex(new_password):
            raise forms.ValidationError("Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character.")

        return cleaned_data

    def is_password_complex(self, password):
        if len(password) < 8:
            return False
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_digit = any(char.isdigit() for char in password)
        has_special = any(char in '!@#$%^&*()-_=+[]{}|;:,.<>?/' for char in password)
        return has_upper, has_lower, has_digit, has_special





