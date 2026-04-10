from django import forms
from django.core.validators import RegexValidator
from books.models import Author, Book, Category, Publisher

class DashboardBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title',
            'isbn',
            'description',
            'image_url',
            'total_quantity',
            'available_quantity',
            'publish_year',
            'publisher',
            'authors',
            'categories',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อหนังสือ'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'เช่น 9786160000000', 'pattern': '[0-9]*', 'inputmode': 'numeric'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'รายละเอียดหนังสือ'}),
            'image_url': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'total_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'available_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'publish_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'เช่น 2566'}),
            'publisher': forms.Select(attrs={'class': 'form-select'}),
            'authors': forms.SelectMultiple(attrs={'id': 'id_authors'}),
            'categories': forms.SelectMultiple(attrs={'id': 'id_categories'}),
        }
        error_messages = {
            'title': {
                'required': 'กรุณากรอกชื่อหนังสือ',
            },
            'isbn': {
                'required': 'กรุณากรอก ISBN',
                'unique': 'มี ISBN นี้ในระบบแล้ว',
                'invalid': 'ISBN ต้องเป็นตัวเลขเท่านั้น'
            },
        }   

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if isbn and not isbn.isdigit():
            raise forms.ValidationError('ISBN ต้องเป็นตัวเลขเท่านั้น')
        return isbn

    def clean(self):
        cleaned_data = super().clean()
        total_quantity = cleaned_data.get('total_quantity')
        available_quantity = cleaned_data.get('available_quantity')

        if total_quantity is not None and available_quantity is not None:
            if available_quantity > total_quantity:
                self.add_error('available_quantity', 'จำนวนพร้อมให้ยืมต้องไม่มากกว่าจำนวนทั้งหมด')

        return cleaned_data


class BaseNamedEntityDashboardForm(forms.ModelForm):
    class Meta:
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อ'}),
        }


class DashboardAuthorForm(BaseNamedEntityDashboardForm):
    class Meta(BaseNamedEntityDashboardForm.Meta):
        model = Author


class DashboardCategoryForm(BaseNamedEntityDashboardForm):
    class Meta(BaseNamedEntityDashboardForm.Meta):
        model = Category


class DashboardPublisherForm(BaseNamedEntityDashboardForm):
    class Meta(BaseNamedEntityDashboardForm.Meta):
        model = Publisher
