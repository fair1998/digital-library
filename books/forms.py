from django import forms
from books.models import Book

class DashboardBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title',
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
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'รายละเอียดหนังสือ'}),
            'image_url': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'total_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'available_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'publish_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'เช่น 2026'}),
            'publisher': forms.Select(attrs={'class': 'form-select'}),
            'authors': forms.SelectMultiple(attrs={'id': 'id_authors'}),
            'categories': forms.SelectMultiple(attrs={'id': 'id_categories'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        total_quantity = cleaned_data.get('total_quantity')
        available_quantity = cleaned_data.get('available_quantity')

        if total_quantity is not None and available_quantity is not None:
            if available_quantity > total_quantity:
                self.add_error('available_quantity', 'จำนวนพร้อมให้ยืมต้องไม่มากกว่าจำนวนทั้งหมด')

        return cleaned_data
