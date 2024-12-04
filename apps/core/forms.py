"""Core form implementations."""
from django import forms

class BaseForm(forms.Form):
    """Base form class with common styling and functionality."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_form_control_class()
    
    def apply_form_control_class(self):
        """Apply Bootstrap form-control class to all fields."""
        for field in self.fields.values():
            css_classes = field.widget.attrs.get('class', '').split()
            if 'form-control' not in css_classes:
                css_classes.append('form-control')
            field.widget.attrs['class'] = ' '.join(css_classes)

class BaseModelForm(forms.ModelForm):
    """Base model form class with common styling and functionality."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_form_control_class()
    
    def apply_form_control_class(self):
        """Apply Bootstrap form-control class to all fields."""
        for field in self.fields.values():
            css_classes = field.widget.attrs.get('class', '').split()
            if 'form-control' not in css_classes:
                css_classes.append('form-control')
            field.widget.attrs['class'] = ' '.join(css_classes)
