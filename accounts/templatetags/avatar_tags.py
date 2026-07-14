from django import template
from django.templatetags.static import static

register = template.Library()

@register.simple_tag
def get_avatar_url(user):
    """
    Get the avatar URL for a user, with fallback to default avatar
    """
    if user.profile_image and user.profile_image.name:
        return user.profile_image.url
    return static('images/default-avatar.png')