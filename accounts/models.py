# Custom User model
class User(AbstractUser):

    # User roles
    class Role(models.TextChoices):
        USER = "user", "User"
        ADMIN = "admin", "Admin"

    # User email
    email = models.EmailField(unique=True)

    # User role: normal user or admin
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER
    )

    # Check if the user's email has been verified
    email_verified = models.BooleanField(default=False)

    # Account creation date
    created_at = models.DateTimeField(auto_now_add=True)


# Stores additional information about each user
class Profile(models.Model):

    # One user can have only one profile
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    # User profile picture
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True
    )

    # User biography
    bio = models.TextField(blank=True)

    # User's preferred theme
    theme = models.CharField(
        max_length=50,
        default="dark"
    )

    # User's preferred font size
    font_size = models.CharField(
        max_length=20,
        default="medium"
    )

    # User's favorite fandom categories
    # Category comes from the catalog app
    favorite_categories = models.ManyToManyField(
        "catalog.Category",
        blank=True,
        related_name="favorite_by_profiles"
    )