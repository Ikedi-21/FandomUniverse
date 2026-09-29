from django import forms
from catalog.forms import ContentSubmissionForm


class StaffContentForm(ContentSubmissionForm):
    is_published = forms.BooleanField(required=False, initial=True, label="Publish immediately")

    class Meta(ContentSubmissionForm.Meta):
        fields = ContentSubmissionForm.Meta.fields + ("release_date", "is_published")
        widgets = {**ContentSubmissionForm.Meta.widgets,
            "release_date": forms.DateTimeInput(attrs={"class": "form-input", "type": "datetime-local"})}
