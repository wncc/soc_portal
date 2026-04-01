import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from accounts.models import UserProfile


def default_season_name():
    now = timezone.now()
    is_winter = now.month >= 10 or now.month <= 2
    return "{}SOC {}".format("W" if is_winter else "", now.year)


# Hard-coded value for the current active season
CURRENT_ACTIVE_SEASON_ID = settings.PORTAL_SETTINGS["CURRENT_ACTIVE_SEASON_ID"]


class SeasonManager(models.Manager):
    def current(self, hard_coded=True):
        if hard_coded:
            return self.get(id=CURRENT_ACTIVE_SEASON_ID)
        return self.get(is_active=True)

    def current_id(self, hard_coded=True):
        if hard_coded:
            return CURRENT_ACTIVE_SEASON_ID
        return self.get(is_active=True).id


def upload_to(instance, filename):
    return "projects/{filename}".format(filename=filename)


class Mentee(models.Model):
    """
    A Mentee is the representation of a user participating in a specific domain as a mentee.
    A single user can be a mentee in multiple domains (one Mentee row per domain).
    """
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        help_text="The user profile corresponding to the mentee.",
    )
    # Domain this mentee record belongs to. Null = legacy SOC (pre-migration).
    domain = models.ForeignKey(
        "domains.Domain",
        on_delete=models.CASCADE,
        related_name="mentees",
        null=True,
        blank=True,
    )
    season = models.TextField(default="1")

    class Meta:
        # One user can only be a mentee once per domain
        unique_together = ("user", "domain")

    def __str__(self):
        domain_str = self.domain.slug if self.domain else "legacy"
        return f"{self.user.roll_number} [{domain_str}]"


class Project(models.Model):

    GeneralCategoryChoices = (
        ("Machine Learning", "Machine Learning"),
        ("Development", "Development"),
        ("Blockchain", "Blockchain"),
        ("Competitive Programming", "Competitive Programming"),
        ("Quant / Finance", "Quant / Finance"),
        ("Robotics / Hardware", "Robotics / Hardware"),
        ("Others", "Others"),
    )

    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, blank=False)

    # Domain this project belongs to. Null = legacy SOC (pre-migration).
    domain = models.ForeignKey(
        "domains.Domain",
        on_delete=models.CASCADE,
        related_name="projects",
        null=True,
        blank=True,
    )

    general_category = models.CharField(
        max_length=255, blank=False, default="Others", choices=GeneralCategoryChoices
    )
    specific_category = models.CharField(max_length=255, blank=False, default="NA")

    mentee_max = models.CharField(max_length=255, blank=False)
    mentor = models.CharField(max_length=255, blank=False, default="NA")
    co_mentor_info = models.TextField(blank=False, default="NA")
    weekly_meets = models.CharField(max_length=255, blank=False, default=0)
    description = models.TextField(blank=False, default="NA")
    timeline = models.TextField(blank=False, default="NA")
    checkpoints = models.TextField(blank=False, default="NA")
    prereuisites = models.TextField(blank=False, default="NA")
    banner_image = models.ImageField(upload_to=upload_to, blank=True, null=True)
    banner_image_link = models.URLField(blank=True, null=True)
    code = models.CharField(max_length=8, editable=False, unique=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)


class MenteeWishlist(models.Model):
    """Wishlist (bookmarks) of a mentee for a domain's projects."""
    mentee = models.ForeignKey(Mentee, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.mentee.user.roll_number + " - " + self.project.title

    class Meta:
        unique_together = ("mentee", "project")


class MenteePreference(models.Model):
    """Formal preferences (with SOP) of a mentee for a domain's projects."""
    mentee = models.ForeignKey(Mentee, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    sop = models.TextField(null=False)
    preference = models.IntegerField(null=False, blank=False)

    def __str__(self):
        return (
            self.mentee.user.roll_number
            + " - "
            + self.project.title
            + " - "
            + str(self.preference)
        )

    class Meta:
        unique_together = [
            ("mentee", "preference"),
            ("mentee", "project"),
        ]


class Mentor(models.Model):
    """
    A Mentor is the representation of a user participating in a specific domain as a mentor.
    A single user can be a mentor in multiple domains (one Mentor row per domain).
    """
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        help_text="The user profile corresponding to the mentor.",
    )
    # Domain this mentor record belongs to. Null = legacy SOC (pre-migration).
    domain = models.ForeignKey(
        "domains.Domain",
        on_delete=models.CASCADE,
        related_name="mentors",
        null=True,
        blank=True,
    )
    season = models.TextField(default="1")

    projects = models.ManyToManyField(
        Project,
        blank=True,
        help_text="Projects that this mentor is leading in this domain.",
        related_name="mentors",
    )

    class Meta:
        # One user can only be a mentor once per domain
        unique_together = ("user", "domain")

    def mentees(self, project_id):
        """Returns a queryset of mentees who have a preference for a given project."""
        return Mentee.objects.filter(
            menteepreference__project_id=project_id
        ).distinct()

    def __str__(self):
        domain_str = self.domain.slug if self.domain else "legacy"
        return f"{self.user.roll_number} [{domain_str}]"


class RankList(models.Model):
    """
    Unified ranking of mentees for a project.

    BREAKING CHANGE from old schema:
    - Old: one RankList per (mentor, mentee, project) — caused merge conflicts for co-mentors
    - New: one RankList per (project, mentee) — all mentors/co-mentors share the same list
    
    Any mentor linked to the project can read/write the ranklist.
    The project-level ranklist is the single source of truth.
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="ranklists",
        help_text="The project this ranking belongs to.",
    )
    mentee = models.ForeignKey(
        Mentee,
        on_delete=models.CASCADE,
        related_name="rankings",
        help_text="The mentee being ranked.",
    )
    rank = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Rank given to this mentee for this project (1 = highest preference).",
    )
    preference = models.PositiveIntegerField(
        help_text="The mentee's own preference number for this project.",
    )

    class Meta:
        # One rank entry per (project, mentee) — no more per-mentor duplicates
        unique_together = ("project", "mentee")
        ordering = ["rank"]
        verbose_name = "Rank List"
        verbose_name_plural = "Rank Lists"

    def __str__(self):
        return (
            f"Project: {self.project.title}, "
            f"Mentee: {self.mentee.user.roll_number}, "
            f"Rank: {self.rank}"
        )

    def get_preference(self):
        """Fetches mentee preference from MenteePreference model."""
        mentee_pref = MenteePreference.objects.filter(
            mentee=self.mentee, project=self.project
        ).first()
        return mentee_pref.preference if mentee_pref else None
