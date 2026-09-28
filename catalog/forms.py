from urllib.parse import urlparse

from django import forms
from django.core.exceptions import ValidationError

from .models import Content


class ContentSubmissionForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ('title', 'category', 'content_type', 'description', 'body', 'genres', 'tags', 'thumbnail', 'video_url', 'file')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-input form-textarea', 'rows': 4}),
            'body': forms.Textarea(attrs={'class': 'form-input form-textarea', 'rows': 6}),
            'genres': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'thumbnail': forms.ClearableFileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
            'video_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-input'}),
        }

    def clean_thumbnail(self):
        image = self.cleaned_data.get('thumbnail')
        if image and image.size > 5 * 1024 * 1024:
            raise ValidationError('Thumbnail must be 5 MB or smaller.')
        return image

    def clean(self):
        cleaned = super().clean()
        video_url = cleaned.get('video_url')
        content_type = cleaned.get('content_type')
        if video_url and content_type == 'video':
            host = (urlparse(video_url).hostname or '').lower()
            if host not in {'youtube.com', 'www.youtube.com', 'm.youtube.com', 'youtu.be', 'vimeo.com', 'www.vimeo.com', 'player.vimeo.com'}:
                self.add_error('video_url', 'Use a YouTube or Vimeo video URL.')
        if content_type in {'video', 'audio'} and not video_url and not cleaned.get('file'):
            self.add_error('file', 'Add a media URL or upload a media file.')
        return cleaned
