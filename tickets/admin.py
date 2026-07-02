from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Ticket, Review, Category, SubCategory

class SubCategoryInline(TabularInline):
    model = SubCategory
    extra = 1

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [SubCategoryInline]

@admin.register(SubCategory)
class SubCategoryAdmin(ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')

@admin.register(Ticket)
class TicketAdmin(ModelAdmin):
    list_display = ('title', 'user', 'category', 'sub_category', 'priority', 'status', 'budget', 'assigned_technician', 'created_at')
    list_filter = ('status', 'priority', 'category', 'sub_category')
    search_fields = ('title', 'description', 'user__name', 'user__email')

@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ('ticket', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('ticket__title', 'comment')
