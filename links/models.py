from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Link(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="links"
    )

    title = models.CharField(max_length=100)
    url = models.URLField()

    icon = models.CharField(max_length=50, blank=True)

    order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]