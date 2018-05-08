from django.contrib import admin
from item.models import Category, Item, Subcategory, Tag


admin.site.register(Item)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Tag)