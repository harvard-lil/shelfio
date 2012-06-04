from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib import auth
import random
from lil.shlvme import utils
from lil.shlvme.fields import UUIDField
from django.forms.widgets import TextInput, Textarea
from django.template.defaultfilters import slugify
from django.utils import simplejson
from django.core.exceptions import ValidationError

class Shelf(models.Model):
    user = models.ForeignKey(User)
    shelf_uuid = UUIDField(auto=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.CharField(max_length=1000)
    creation_date = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        slug = slugify(self.name)
        if Shelf.objects.filter(user=self.user, slug=slug).exclude(pk=self.pk).exists():
            raise ValidationError('You already have a shelf by that name.')
        else:
            self.slug = slugify(self.name)
            super(Shelf, self).save(*args, **kwargs)

class Item(models.Model):
    shelf = models.ForeignKey(Shelf)
    item_uuid = UUIDField(auto=True)
    title = models.CharField(max_length=200)
    link = models.URLField()
    measurement_page_numeric = models.PositiveIntegerField(default=300)
    measurement_height_numeric = models.DecimalField(default='25.5', max_digits=5, decimal_places=2)
    format = models.CharField(max_length=200)
    shelfrank = models.PositiveIntegerField(default=random.randint(0, 100))
    creation_date = models.DateTimeField(auto_now=True)
    pub_date = models.PositiveIntegerField(default=utils.get_current_year())
    sort_order = models.PositiveIntegerField(editable=False) 

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            try:
                max = Item.objects.order_by('-sort_order')[0].sort_order
                self.sort_order = max + 1
            except IndexError:
                self.sort_order = 1
        super(Item, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-sort_order']
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

class EmailInput(TextInput):
    input_type = 'email'

class EditProfileForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=False, widget=EmailInput)

class NewShelfForm(forms.Form):
    name = forms.CharField(max_length=200)
    description = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={'rows': '4'}),
    )
    is_public = forms.BooleanField(required=False)

class AddItemForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(AddItemForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['shelf'].queryset = Shelf.objects.filter(user=user)
            self.fields['shelf'].empty_label = None
    class Meta:
        model = Item

class CreatorForm(forms.Form):
    creator = forms.CharField(max_length=1000)
    
class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        exclude = ('item')