from django import forms
from .models import FanSubmission, EventHighlight

MAX_IMAGE = 2 * 1024 * 1024


class FanSubmissionForm(forms.ModelForm):
    class Meta:
        model = FanSubmission
        fields = ('title', 'category', 'body', 'image')

    def clean_body(self):
        body = self.cleaned_data['body'].strip()
        if len(body) < 50:
            raise forms.ValidationError('Please write at least 50 characters.')
        return body

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size > MAX_IMAGE:
            raise forms.ValidationError('Image must be under 2 MB.')
        return image


class HighlightForm(forms.ModelForm):
    class Meta:
        model = EventHighlight
        fields = ('category', 'title', 'body', 'event_date', 'image', 'display_order')
        widgets = {'event_date': forms.DateInput(attrs={'type': 'date'})}