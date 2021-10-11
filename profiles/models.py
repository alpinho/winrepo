import random
import string

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone

from django.urls import reverse

from multiselectfield import MultiSelectField

PHD = 'PhD student'
MDR = 'Medical Doctor'
PDR = 'Post-doctoral researcher'
JRE = 'Researcher/ scientist'
SRE = 'Senior researcher/ scientist'
LEC = 'Lecturer'
ATP = 'Assistant Professor'
ACP = 'Associate Professor'
PRF = 'Professor'
DIR = 'Group leader/ Director/ Head of Department'

POSITION_CHOICES = (
    (PHD, 'PhD student'),
    (MDR, 'Medical Doctor'),
    (PDR, 'Post-doctoral researcher'),
    (JRE, 'Researcher/ scientist'),
    (SRE, 'Senior researcher/ scientist'),
    (LEC, 'Lecturer'),
    (ATP, 'Assistant Professor'),
    (ACP, 'Associate Professor'),
    (PRF, 'Professor'),
    (DIR, 'Group leader/ Director/ Head of Department')
)

MONTHS_CHOICES = (
    ('01', 'January'),
    ('02', 'February'),
    ('03', 'March'),
    ('04', 'April'),
    ('05', 'May'),
    ('06', 'June'),
    ('07', 'July'),
    ('08', 'August'),
    ('09', 'September'),
    ('10', 'October'),
    ('11', 'November'),
    ('12', 'December')
)

STRUCTURE_CHOICES = (
    ('N', 'Neuron'),
    ('L', 'Layer'),
    ('C', 'Column'),
    ('R', 'Region'),
    ('W', 'Whole Brain')
)

MODALITIES_CHOICES = (
    ('EP', 'Electrophysiology (EEG, MEG, ECoG)'),
    ('OE', 'Other electrophysiology'),
    ('MR', 'MRI'),
    ('PE', 'PET'),
    ('DT', 'DTI'),
    ('BH', 'Behavioural'),
    ('ET', 'Eye Tracking'),
    ('BS', 'Brain Stimulation'),
    ('GT', 'Genetics'),
    ('FN', 'fNIRS'),
    ('LE', 'Lesions and Inactivations'),
)

METHODS_CHOICES = (
    ('UV', 'Univariate'),
    ('MV', 'Multivariate'),
    ('PM', 'Predictive Models'),
    ('DC', 'DCM'),
    ('CT', 'Connectivity'),
    ('CM', 'Computational Modeling'),
    ('AM', 'Animal Models')
)

DOMAINS_CHOICES = (
    ('CG', 'Cognition (general)'),
    ('MM', 'Memory'),
    ('SS', 'Sensory systems'),
    ('MO', 'Motor Systems'),
    ('LG', 'Language'),
    ('EM', 'Emotion'),
    ('PN', 'Pain'),
    ('LE', 'Learning'),
    ('AT', 'Attention'),
    ('DE', 'Decision Making'),
    ('DV', 'Developmental'),
    ('SL', 'Sleep'),
    ('CN', 'Consciousness'),
    ('CL', 'Clinical (general)'),
    ('DM', 'Dementia'),
    ('PK', 'Parkinson'),
    ('DD', 'Other degenerative diseases'),
    ('PS', 'Psychiatry'),
    ('AD', 'Addiction'),
    ('ON', 'Oncology'),
    ('EV', 'Evolutionary'),
    ('CM', 'Cellular and Molecular'),
    ('BI', 'Bioinformatics'),
    ('NC', 'Neuropharmacology'),
    ('ET', 'Ethics')
)


class Country(models.Model):
    code = models.CharField(max_length=3, blank=False, unique=True)
    name = models.CharField(max_length=60, blank=False)
    is_under_represented = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'countries'
        ordering = ['name']

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))

        extra_fields.setdefault('is_active', True)
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    username = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'username'

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def first_name(self):
        return self.name.split(' ', 1)[0]

    @property
    def any_claimed_profile(self):
        try:
            Profile.all_objects.values('id').get(
                claimed_by=self,
                claimed_at__isnull=False
            )
            return True
        except Profile.DoesNotExist:
            return False


class ProfileManager(models.Manager):

    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return ProfileQuerySet(self.model).filter(deleted_at=None)
        return ProfileQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()


class ProfileQuerySet(QuerySet):
    def delete(self):
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(deleted_at=None)

    def dead(self):
        return self.exclude(deleted_at=None)


class Profile(models.Model):

    objects = ProfileManager()
    all_objects = ProfileManager(alive_only=False)

    @classmethod
    def get_position_choices(cls):
        return POSITION_CHOICES

    @classmethod
    def get_structure_choices(cls):
        return STRUCTURE_CHOICES

    @classmethod
    def get_modalities_choices(cls):
        return MODALITIES_CHOICES

    @classmethod
    def get_methods_choices(cls):
        return METHODS_CHOICES

    @classmethod
    def get_domains_choices(cls):
        return DOMAINS_CHOICES

    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        null=True, blank=True, related_name='profile'
    )
    is_public = models.BooleanField(default=True)
    
    name = models.CharField(max_length=200, blank=False)
    contact_email = models.EmailField(verbose_name='Contact E-mail', blank=True)
    webpage = models.URLField(blank=True)
    institution = models.CharField(max_length=100, blank=False)
    country = models.ForeignKey(Country,
                                on_delete=models.CASCADE,
                                related_name='profiles',
                                null=True)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES,
                                blank=True)
    grad_month = models.CharField(max_length=2, choices=MONTHS_CHOICES,
                                  blank=True)
    grad_year = models.CharField(max_length=4, blank=True)
    brain_structure = MultiSelectField(choices=STRUCTURE_CHOICES, blank=True)
    modalities = MultiSelectField(choices=MODALITIES_CHOICES, blank=True)
    methods = MultiSelectField(choices=METHODS_CHOICES, blank=True)
    domains = MultiSelectField(choices=DOMAINS_CHOICES, blank=True)
    keywords = models.CharField(max_length=250, blank=True)

    orcid = models.CharField(verbose_name='ORCID', help_text='Please insert the information from the brackets: https://orcid.org/[ID]', max_length=30, blank=True)
    twitter = models.CharField(max_length=200, help_text='Please insert the information from the brackets: https://twitter.com/[username]', blank=True)
    linkedin = models.CharField(verbose_name='Linked-in', help_text='Please insert the information from the brackets: https://linkedin.com/in/[username]', max_length=200, blank=True)
    github = models.CharField(max_length=200, blank=True, help_text='Please insert the information from the brackets: https://github.com/[username]')
    google_scholar = models.CharField(verbose_name='Google Scholar', help_text='Please insert the information from the brackets: https://scholar.google.com/citations?user=[ID]', max_length=200, blank=True)
    researchgate = models.CharField(verbose_name='ResearchGate', help_text='Please insert the information from the brackets: https://www.researchgate.net/profile/[username]', max_length=200, blank=True)

    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    claimed_at = models.DateTimeField(null=True)
    claimed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        related_name='profile_claims',
        null=True
    )

    class Meta:
        ordering = ['name', 'institution', 'updated_at']
        base_manager_name = 'objects'

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super().delete()

    def __str__(self):
        return f'{self.name}, {self.institution}'

    def brain_structure_labels(self):
        return [dict(STRUCTURE_CHOICES).get(item, item)
                for item in self.brain_structure]

    def modalities_labels(self):
        return [dict(MODALITIES_CHOICES).get(item, item)
                for item in self.modalities]

    def methods_labels(self):
        return [dict(METHODS_CHOICES).get(item, item)
                for item in self.methods]

    def domains_labels(self):
        return [dict(DOMAINS_CHOICES).get(item, item)
                for item in self.domains]

    def grad_month_labels(self):
        return dict(MONTHS_CHOICES).get(self.grad_month)


class Recommendation(models.Model):
    PHD = 'PhD student'
    MDR = 'Medical Doctor'
    PDR = 'Post-doctoral researcher'
    SRE = 'Senior researcher/ scientist'
    LEC = 'Lecturer'
    ATP = 'Assistant Professor'
    ACP = 'Associate Professor'
    PRF = 'Professor'
    DIR = 'Group leader/ Director/ Head of Department'

    POSITION_CHOICES = (
        (PHD, PHD),
        (MDR, MDR),
        (PDR, PDR),
        (SRE, SRE),
        (LEC, LEC),
        (ATP, ATP),
        (ACP, ACP),
        (PRF, PRF),
        (DIR, DIR),
    )

    profile = models.ForeignKey(Profile,
                                on_delete=models.CASCADE,
                                related_name='recommendations')
    reviewer_name = models.CharField(max_length=100, blank=False)
    reviewer_email = models.EmailField(blank=True)
    reviewer_position = models.CharField(max_length=50,
                                         choices=POSITION_CHOICES,
                                         blank=True)
    reviewer_institution = models.CharField(max_length=100, blank=False)
    seen_at_conf = models.BooleanField(null=True)
    comment = models.TextField(blank=False)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.comment[:50]
