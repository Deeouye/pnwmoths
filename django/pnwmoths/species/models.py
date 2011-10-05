import datetime
from sorl.thumbnail import ImageField
from tastypie.models import create_api_key

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.localflavor.ca.ca_provinces import PROVINCE_CHOICES
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.db import models


models.signals.post_save.connect(create_api_key, sender=User)


class State(models.Model):
    choices = STATE_CHOICES + PROVINCE_CHOICES
    code = models.CharField(unique=True, choices=choices, max_length=2)

    class Meta:
        ordering = ["code"]

    def __unicode__(self):
        return self.get_code_display()


class County(models.Model):
    state = models.ForeignKey(State)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        unique_together = ("state", "name")
        verbose_name_plural = u"counties"

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.state.code)


class Collector(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __unicode__(self):
        return self.name


class Collection(models.Model):
    """
    Represents a location where a species record may be kept in storage.
    """
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __unicode__(self):
        return self.name


class Species(models.Model):
    """
    Represents a species with a near-constant genus and species name.

    TODO: handle general key/value attributes including discoverer/year,
    synonyms, location on plates, NOC code, etc.
    """
    genus = models.CharField(max_length=255)
    species = models.CharField(max_length=255)
    common_name = models.CharField(max_length=255, blank=True, null=True)
    similar = models.ManyToManyField("self", blank=True)

    class Meta:
        ordering = ["genus", "species"]
        unique_together = ("genus", "species")
        verbose_name_plural = u"species"

    def __unicode__(self):
        if self.common_name:
            name = u"%s %s (%s)" % (self.genus, self.species, self.common_name)
        else:
            name = u"%s %s" % (self.genus, self.species)

        return name

    @property
    def name(self):
        return unicode(self)

    def get_first_image(self):
        """
        Return the first image of this species' images if one exists and None
        otherwise.

        TODO: turn this into a m2m manager method for SpeciesImage
        """
        try:
            return self.speciesimage_set.all()[0]
        except:
            return None


class SpeciesRecord(models.Model):
    """
    Represents a single record of a species based on a combination of where and
    when the specimen was found and by whom. At the minimum, a species record
    must include latitude and longitude values.

    The following fields define a unique record despite the fact that most of
    these fields can be empty:

    species,
    latitude,
    longitude,
    year,
    month,
    day,
    collector,
    collection,
    notes
    """
    # Set the number of decimal points to include in longitude and latitude
    # values returned to the user.
    GPS_PRECISION = 2

    species = models.ForeignKey(Species)
    latitude = models.FloatField()
    longitude = models.FloatField()

    locality = models.CharField(null=True, blank=True, max_length=255)
    county = models.ForeignKey(County, null=True, blank=True)
    state = models.ForeignKey(State, null=True, blank=True)
    elevation = models.IntegerField(help_text="measured in feet", null=True,
                                    blank=True)
    year = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    day = models.IntegerField(null=True, blank=True)

    collector = models.ForeignKey(Collector, null=True, blank=True)
    collection = models.ForeignKey(Collection, null=True, blank=True)
    males = models.IntegerField(null=True, blank=True)
    females = models.IntegerField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    date_added = models.DateTimeField(editable=False)
    date_modified = models.DateTimeField(editable=False)

    class Meta:
        ordering = ("species", "latitude", "longitude")

    def __unicode__(self):
        return u"%s at (%.2f, %.2f)" % (self.species, self.latitude, self.longitude)

    @property
    def date(self):
        try:
            date = datetime.date(self.year, self.month, self.day)
        except ValueError:
            date = None

        return date

    def save(self, *args, **kwargs):
        if not self.date_added:
            self.date_added = datetime.datetime.now()
        self.date_modified = datetime.datetime.now()

        super(SpeciesRecord, self).save(*args, **kwargs)


class SpeciesImage(models.Model):
    """
    Represents an image of a specific species.
    """
    IMAGE_PATH = "moths/"
    SIZES = {
        "thumbnail": "140x93",
        "medium": "375x249"
    }

    species = models.ForeignKey(Species)
    # Image field manages the creation and deletion of thumbnails
    # automatically. When an instance of this class is deleted, thumbnails
    # created for this field are automatically deleted too.
    image = ImageField(upload_to=IMAGE_PATH)
    record = models.ForeignKey(SpeciesRecord, blank=True, null=True)

    def __unicode__(self):
        return self.image.name

    def title(self):
        return self.species


# TODO: write unit tests for this class before adding it.
# class SpeciesImageMetadata(models.Model):
#     """
#     Represents key/value metadata associated with a specific species image.

#     Examples include order, orientation (ventral, dorsal, etc.), photographer,
#     developmental stage of the individual, etc.
#     """
#     key = models.CharField(max_value=255)
#     value = models.CharField(max_value=255)
