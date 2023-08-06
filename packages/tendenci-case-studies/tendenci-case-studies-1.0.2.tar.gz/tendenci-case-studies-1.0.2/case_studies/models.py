from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from tendenci.core.perms.object_perms import ObjectPermission
from tagging.fields import TagField
from tendenci.core.perms.models import TendenciBaseModel
from case_studies.managers import CaseStudyManager

from tendenci.core.files.models import File
from tendenci.core.files.managers import FileManager


class CaseStudy(TendenciBaseModel):
    client = models.CharField(max_length=75)
    website = models.URLField(max_length=150)
    slug = models.SlugField(max_length=100)
    overview = models.TextField(blank=True, null=True)
    execution = models.TextField(blank=True, null=True)
    results = models.TextField(blank=True, null=True)
    tags = TagField(blank=True, help_text=_('Tags separated by commas. E.g Tag1, Tag2, Tag3'))
    
    perms = generic.GenericRelation(ObjectPermission,
                                          object_id_field="object_id",
                                          content_type_field="content_type")

    objects = CaseStudyManager()

    def __unicode__(self):
        return self.client

    class Meta:
        permissions = (("view_casestudy","Can view case study"),)
        verbose_name = 'Case Study'
        verbose_name_plural = 'Case Studies'

    def delete(self, *args, **kwargs):
        for img in self.image_set.all():
            img.delete()
        return super(CaseStudy, self).delete(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ("case_study.view", [self.slug])
        
    def featured_screenshots(self):
        try:
            return self.image_set.filter(file_type='featured')
        except:
            return False
    
    def screenshots(self):
        try:
            return self.image_set.filter(file_type='screenshot')
        except:
            return False
            
    def other_images(self):
        try:
            return self.image_set.filter(file_type='other')
        except:
            return False
            
    def homepage_images(self):
        try:
            return self.image_set.filter(file_type='homepage')
        except:
            return False

class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']

    @models.permalink
    def get_absolute_url(self):
        return ("case_study.service", [self.pk])


class Technology(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name = "Technology"
        verbose_name_plural = "Technologies"

    @models.permalink
    def get_absolute_url(self):
        return ("case_study.technology", [self.pk])

class Image(File):
    case_study = models.ForeignKey(CaseStudy)
    file_ptr = models.OneToOneField(File, related_name="%(app_label)s_%(class)s_related")
    file_type = models.CharField(
        _('File type'),
        max_length=50,
        choices=(
            ('featured','Featured Screenshot'),
            ('screenshot','Screenshot'),
            ('homepage', 'Homepage Image'),
            ('other','Other'),
        ),
        default='other',
    )
    position = models.IntegerField(blank=True)

    objects = FileManager()

    def save(self, *args, **kwargs):
        if self.position is None:
            # Append
            try:
                last = Image.objects.order_by('-position')[0]
                self.position = last.position + 1
            except IndexError:
                # First row
                self.position = 0

        return super(Image, self).save(*args, **kwargs)

    class Meta:
        ordering = ('position',)
