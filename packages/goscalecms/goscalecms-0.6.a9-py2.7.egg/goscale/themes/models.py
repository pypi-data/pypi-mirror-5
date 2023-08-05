import tarfile
import StringIO
import shutil
import os

from django.conf import settings
from django.db import models
from django.contrib.sites.models import Site
from django.db.models.signals import post_save, pre_save, post_delete, m2m_changed
from django.utils.translation import ugettext, ugettext_lazy as _
from cms.models import Page
from goscale.themes import set_themes

class Theme(models.Model):
    """
    Goscale CMS theme
    """
    sites = models.ManyToManyField(Site, related_name='themes', null=True, blank=True)
    name = models.CharField(max_length=255, blank=True, help_text=_(
        'Only set name if no theme file provided (should be consistent with directory name).'
    ))
    theme_file = models.FileField(upload_to='themes_archives', null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.id and not self.name:
            f = tarfile.open(fileobj=self.theme_file, mode='r:gz')
            self.name = f.getnames()[-1]
            f.extractall(settings.THEMES_DIR)

        super(Theme, self).save(*args, **kwargs)

    def get_sites(self):
        """
        Returns all sites using this theme
        """
        return self.sites.all()

    def get_site(self):
        """
        Returns first site using this theme
        """
        try:
            return self.get_sites()[0]
        except IndexError:
            return None
                
    
    class Meta:
        verbose_name = "Theme"
        verbose_name_plural = "Themes"

    def __unicode__(self):
        return self.name

def delete_themes(sender, **kwargs):
    instance = kwargs['instance']
    try:
        shutil.rmtree(os.path.join(settings.THEMES_DIR, instance.name))
    except OSError: 
        pass
    set_themes()

def theme_site_m2m_changes(sender, **kwargs):
    instance = kwargs['instance']
    action = kwargs['action']
    if action in ("post_add", "post_remove", "post_clear"):
        if type(instance) is Theme:
            for site in instance.sites.all():
                for theme in site.themes.all():
                    if theme.id != instance.id:
                        site.theme_set.remove(theme)        
        set_themes()
post_delete.connect(delete_themes, sender=Theme)
m2m_changed.connect(theme_site_m2m_changes, sender=Theme.sites.through)
