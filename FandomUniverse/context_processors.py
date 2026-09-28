from accounts.models import Profile

def user_preferences(request):
    """Expose saved display preferences without changing the page layouts."""
    theme = 'light'
    user_theme = ''
    font_size = '16px'
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None
        if profile:
            if profile.theme in {'dark', 'light'}:
                theme = profile.theme
                user_theme = profile.theme
            font_size = {'small': '14px', 'medium': '16px', 'large': '19px'}.get(profile.font_size, '16px')
    return {'site_theme': theme, 'site_user_theme': user_theme, 'site_font_size': font_size}
