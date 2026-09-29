from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, UserCreationForm
from django.core.exceptions import ValidationError
from .models import Profile, Avatar

User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-input'})
        self.fields['username'].widget.attrs.update({'autocomplete': 'username'})
        self.fields['email'].widget.attrs.update({'autocomplete': 'email'})
        self.fields['password1'].widget.attrs.update({'autocomplete': 'new-password'})
        self.fields['password2'].widget.attrs.update({'autocomplete': 'new-password'})

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email


class VerifiedAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.email_verified and not user.is_staff:
            raise ValidationError(
                "Please verify your email before logging in. Check your inbox, or request a new link.",
                code='email_not_verified',
            )


class StyledPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-input', 'placeholder': 'you@example.com',
            'autocomplete': 'email',
        })


class ProfileForm(forms.ModelForm):
    theme = forms.ChoiceField(choices=[('dark', 'Dark'), ('light', 'Light')])
    font_size = forms.ChoiceField(choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')])
    favorite_categories = forms.ModelMultipleChoiceField(
        queryset=Profile._meta.get_field('favorite_categories').remote_field.model.objects.none(),
        required=False, widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Profile
        fields = ('bio', 'theme', 'font_size', 'avatar', 'custom_avatar', 'favorite_categories')
        widgets = {'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-input form-textarea'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from catalog.models import Category
        self.fields['favorite_categories'].queryset = Category.objects.order_by('name')
        self.fields['avatar'].queryset = Avatar.objects.filter(is_active=True)
        self.fields['avatar'].required = False
        self.fields['custom_avatar'].required = False
        self.fields['theme'].widget.attrs.update({'class': 'form-select'})
        self.fields['font_size'].widget.attrs.update({'class': 'form-select'})
        self.fields['avatar'].widget.attrs.update({'class': 'form-select'})
        self.fields['custom_avatar'].widget.attrs.update({'accept': 'image/*'})

    def clean_custom_avatar(self):
        image = self.cleaned_data.get('custom_avatar')
        if image and image.size > 2 * 1024 * 1024:
            raise ValidationError('Choose an image no larger than 2 MB.')
        return image
