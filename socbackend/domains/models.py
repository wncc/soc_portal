from django.db import models
from django.conf import settings


def upload_domain_cover(instance, filename):
    return f"domain_covers/{instance.slug}/{filename}"


class Domain(models.Model):
    """
    Represents a tech domain managed under Summer of Tech.
    e.g., SOC (Summer of Code), SOQ (Summer of Quants), SOR (Summer of Robotics)
    """
    slug = models.CharField(max_length=20, unique=True, help_text="Short identifier, e.g. 'soc', 'soq'")
    name = models.CharField(max_length=100, help_text="Full name, e.g. 'Summer of Code'")
    description = models.TextField(blank=True, default="")
    cover_photo = models.ImageField(upload_to=upload_domain_cover, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    mentee_reg_open = models.BooleanField(default=False, help_text="Open for mentees to self-register")
    mentor_reg_open = models.BooleanField(default=False, help_text="Open for mentors to self-register (pending approval)")
    project_creation_open = models.BooleanField(default=True, help_text="Allow mentors to create new projects")
    project_editing_open = models.BooleanField(default=True, help_text="Allow mentors to edit existing projects")
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0, help_text="Display ordering (lower = first)")


    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name} ({self.slug})"


class DomainMembership(models.Model):
    """
    Represents a user's role within a specific domain.
    A user can hold multiple roles across multiple domains:
      e.g., manager of SOC, mentee of SOQ, mentor of SOR
    
    domain=None means platform-level manager (manages all domains).
    """
    ROLE_CHOICES = [
        ("mentor", "Mentor"),
        ("mentee", "Mentee"),
        ("manager", "Manager"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="domain_memberships",
    )
    domain = models.ForeignKey(
        Domain,
        on_delete=models.CASCADE,
        related_name="memberships",
        null=True,
        blank=True,
        help_text="Null means platform-level manager with access to all domains",
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    joined = models.DateTimeField(auto_now_add=True)
    # Mentor applications start as unapproved; manager approves them.
    # Mentee self-registrations and manager grants are auto-approved.
    is_approved = models.BooleanField(
        default=False,
        help_text="Whether this membership has been approved by a domain manager",
    )

    class Meta:
        unique_together = ("user", "domain", "role")
        ordering = ["-joined"]

    def __str__(self):
        domain_str = self.domain.slug if self.domain else "ALL"
        return f"{self.user.username} — {self.role} in {domain_str}"
