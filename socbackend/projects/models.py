import uuid

from django.conf import settings
from django.core.validators import  MinValueValidator
from django.db import models
from django.utils import timezone

from accounts.models import UserProfile


def default_season_name():
    now = timezone.now()
    is_winter = now.month >= 10 or now.month <= 2
    return "{}SOC {}".format("W" if is_winter else "", now.year)


# Hard-coded value for the current active season, since we assume this doesn't change over a long period
CURRENT_ACTIVE_SEASON_ID = settings.PORTAL_SETTINGS["CURRENT_ACTIVE_SEASON_ID"]


class SeasonManager(models.Manager):
    def current(self, hard_coded=True):
        """
        Method to get the currently active Season. Has a hacky implementation using the
        hard-coded Season ID, which can be overriden by setting hard_coded to False
        """
        if hard_coded:
            return self.get(id=CURRENT_ACTIVE_SEASON_ID)
        return self.get(is_active=True)

    def current_id(self, hard_coded=True):
        """
        Method to get the currently active Season ID. Has a hacky implementation using the
        hard-coded Season ID, which can be overriden by setting hard_coded to False
        """
        if hard_coded:
            return CURRENT_ACTIVE_SEASON_ID
        return self.get(is_active=True).id


def upload_to(instance, filename):
    return "projects/{filename}".format(filename=filename)



class Mentee(models.Model):
    """
    A Mentee is the representation of a user in a season applying to projects.
    """

    user = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        help_text="The user corresponding to the mentee.",
        unique=True,
    )
    season = models.TextField(default='1')

    def __str__(self):
        return self.user.roll_number
    


class Project(models.Model):

    GeneralCategoryChoices = (
        ('ML', 'ML'),
        ('Development', 'Development'),
        ('Blockchain', 'Blockchain'),
        ('CP', 'CP'),
        ('Others', 'Others'),
    )


    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, blank=False)

    general_category = models.CharField(max_length=255, blank=False, default='Others', choices=GeneralCategoryChoices)

    specific_category = models.CharField(max_length=255, blank=False, default='NA')


    mentee_max = models.CharField(max_length=255, blank=False)
    mentor = models.CharField(max_length=255, blank=False, default="NA")
    co_mentor_info = models.TextField()
    weekly_meets = models.CharField(max_length=255,blank=False,default=0)
    description = models.TextField(blank=False, default="NA")
    timeline = models.TextField(blank=False, default="NA")
    checkpoints = models.TextField(blank=False, default="NA")
    prereuisites = models.TextField(blank=False, default="NA")
    co_mentor_info = models.TextField(blank=False, default="NA")  
    banner_image = models.ImageField(upload_to=upload_to, blank=True, null=True)
    banner_image_link = models.URLField(blank=True, null=True)
    code = models.CharField(max_length=8, editable=False, unique=True)
    # is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code:
            # Generate a UUID and take the first 8 characters
            self.code = str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)


class MenteeWishlist(models.Model):
    """
    Preferences of a mentee (ie a user during a specific season)
    """
    mentee = models.ForeignKey(Mentee, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # sop = models.TextField()
    # preference = models.IntegerField()
    def __str__(self):
        return self.mentee.user.roll_number + " - " + self.project.title
    
    class Meta:
        unique_together = ('mentee', 'project')

        

class MenteePreference(models.Model):
    """
    Preferences of a mentee (ie a user during a specific season)
    """
    mentee = models.ForeignKey(Mentee, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    sop = models.TextField(null=False)
    preference = models.IntegerField(null=False, blank=False)

    def __str__(self):
        return self.mentee.user.roll_number + " - " + self.project.title + " - " + str(self.preference)

    class Meta:
        unique_together = [
            ('mentee', 'project', 'preference'),
            ('mentee', 'project'),
        ]


class Mentor(models.Model):
    """
    A Mentee is the representation of a user in a season applying to projects.
    """

    user = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        help_text="The user corresponding to the mentor.",
        unique=True,
    )
    season = models.TextField(default='1')

    projects = models.ManyToManyField(
        Project,  # Reference to the Project model
        blank=True,  # Make this field optional
        help_text="The project that the mentor is leading.",
        related_name='mentors'  # Use a unique related_name
    )

    def mentees(self,project_id):
        """
        Returns a queryset of mentees who have a preference for the mentor's project.
        """

        mentees_qs = Mentee.objects.filter(
            menteepreference__project_id=project_id
        ).distinct()


        return mentees_qs
    # season = models.ForeignKey(
    #     Season,
    #     on_delete=models.PROTECT,
    #     default=get_current_id,
    #     help_text="The season to which mentee is applying for.",
    # )

    # project = models.ForeignKey(
    #     Project,
    #     null=True,
    #     on_delete=models.SET_NULL,
    #     help_text="The project that the mentee has been selected for. Is NULL if not selected yet.",
    # )

    # preferences = models.ManyToManyField(
    #     "Project",
    #     through="MenteePreference",
    #     related_name="applications",
    #     help_text="The projects that the mentee has applied to.",
    # )


    def __str__(self):
        return self.user.roll_number

class RankList(models.Model):
    """
    Model representing the ranking of mentees by mentors for specific projects.
    """
    mentor = models.ForeignKey(
        Mentor,
        on_delete=models.CASCADE,
        related_name='ranklists',
        help_text="The mentor who ranked the mentee."
    )
    
    mentee = models.ForeignKey(
        Mentee,
        on_delete=models.CASCADE,
        related_name='rankings',
        help_text="The mentee who is ranked by the mentor."
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='ranklists',
        help_text="The project associated with the ranking."
    )
    rank = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="The rank given by the mentor to the mentee for this project."
    )
    preference = models.PositiveIntegerField(
        help_text="The preference given of mentee for this project."
    )

    class Meta:
        unique_together = ('mentor', 'mentee', 'project','preference')
        ordering = ['rank']
        verbose_name = "Rank List"
        verbose_name_plural = "Rank Lists"

    def __str__(self):
        return (f"Project: {self.project.title}, Mentor: {self.mentor.user.roll_number}, "
                f"Mentee: {self.mentee.user.roll_number}, Rank: {self.rank}, Preference: {self.preference}")

    def get_preference(self):
        """Fetches mentee preference from MenteePreference model"""
        mentee_pref = MenteePreference.objects.filter(mentee=self.mentee, project=self.project).first()
        return mentee_pref.preference if mentee_pref else None
