from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
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

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('รหัสผ่านทั้งสองช่องไม่ตรงกัน')
            
            # Custom validation with Thai error messages
            try:
                validate_password(password2, self.instance)
            except ValidationError as error:
                # Translate error messages to Thai
                thai_errors = []
                for err in error.messages:
                    if 'too similar' in err.lower():
                        thai_errors.append('รหัสผ่านมีความคล้ายคลึงกับชื่อผู้ใช้มากเกินไป')
                    elif 'too short' in err.lower() or 'at least 8 characters' in err.lower():
                        thai_errors.append('รหัสผ่านสั้นเกินไป ต้องมีอย่างน้อย 8 ตัวอักษร')
                    elif 'too common' in err.lower():
                        thai_errors.append('รหัสผ่านนี้ใช้กันทั่วไปเกินไป กรุณาเลือกรหัสผ่านที่ปลอดภัยกว่านี้')
                    elif 'entirely numeric' in err.lower():
                        thai_errors.append('รหัสผ่านต้องไม่เป็นตัวเลขล้วน')
                    else:
                        thai_errors.append(err)
                raise forms.ValidationError(thai_errors)
        
        return password2

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
