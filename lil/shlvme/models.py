from django.db import models
from django import forms
from django.contrib.auth.models import User
import random
from lil.shlvme import utils
from lil.shlvme.fields import UUIDField

class Shelf(models.Model):
    user = models.ForeignKey(User)
    shelf_uuid = UUIDField(auto=True)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    creation_date = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField()

    def __unicode__(self):
        return self.name

class Item(models.Model):
    shelf = models.ForeignKey(Shelf)
    item_uuid = UUIDField(auto=True)
    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=200)
    link = models.URLField()
    measurement_page_numeric = models.PositiveIntegerField(default=300)
    measurement_height_numeric = models.DecimalField(default='25.5', max_digits=5, decimal_places=2)
    content_type = models.CharField(max_length=200)
    shelfrank = models.PositiveIntegerField(default=random.randint(0, 100))
    creation_date = models.DateTimeField(auto_now=True)
    pub_date = models.PositiveIntegerField(default=utils.get_current_year())
    sort_order = models.PositiveIntegerField(default=random.randint(0, 100)) 

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['sort_order']
        models.CharField(max_length=200)
        
class Creator(models.Model):
    item = models.ForeignKey(Item)
    creator_uuid = UUIDField(auto=True)
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name
    
class Tag(models.Model):
    item = models.ForeignKey(Item)
    tag_uuid = UUIDField(auto=True)
    key = models.CharField(max_length=200)
    value = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.key
    
#Forms:
class AddToShelfConfirmForm(forms.Form):
    shelf = forms.ModelChoiceField(queryset=Shelf.objects.all())
    title = forms.CharField(max_length=300)
    author = forms.CharField(max_length=100)
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), max_length=100)