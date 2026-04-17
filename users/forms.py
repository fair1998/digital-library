from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    """Form for user registration with citizen ID and phone number"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    phone_number = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'เบอร์โทรศัพท์ (10 หลัก)'
        })
    )
    citizen_id = forms.CharField(
        max_length=13,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'เลขบัตรประชาชน (13 หลัก)'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'citizen_id', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ชื่อผู้ใช้'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ชื่อ'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'นามสกุล'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['phone_number'].required = True
        self.fields['citizen_id'].required = True

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'รหัสผ่าน'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'ยืนยันรหัสผ่าน'
        })

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number:
            raise forms.ValidationError('กรุณากรอกเบอร์โทรศัพท์')
        if not phone_number.isdigit():
            raise forms.ValidationError('เบอร์โทรศัพท์ต้องเป็นตัวเลขเท่านั้น')
        if len(phone_number) != 10:
            raise forms.ValidationError('เบอร์โทรศัพท์ต้องมี 10 หลัก')
        return phone_number

    def clean_citizen_id(self):
        citizen_id = self.cleaned_data.get('citizen_id')
        if not citizen_id:
            raise forms.ValidationError('กรุณากรอกเลขบัตรประชาชน')
        if not citizen_id.isdigit() or len(citizen_id) != 13:
            raise forms.ValidationError('เลขบัตรประชาชนต้องเป็นตัวเลข 13 หลัก')
        return citizen_id

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """Custom login form with Bootstrap styling"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ชื่อผู้ใช้'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'รหัสผ่าน'
        })
    )


class UserProfileForm(forms.ModelForm):
    """Form for users to edit their own profile"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    phone_number = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'เบอร์โทรศัพท์ (10 หลัก)'
        })
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ชื่อ'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'นามสกุล'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['phone_number'].required = True

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number:
            raise forms.ValidationError('กรุณากรอกเบอร์โทรศัพท์')
        if not phone_number.isdigit():
            raise forms.ValidationError('เบอร์โทรศัพท์ต้องเป็นตัวเลขเท่านั้น')
        if len(phone_number) != 10:
            raise forms.ValidationError('เบอร์โทรศัพท์ต้องมี 10 หลัก')
        return phone_number
