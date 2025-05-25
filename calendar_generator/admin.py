from django.contrib import admin
from django.utils.html import format_html

from .models import Holiday, CalendarGeneration, ArtworkOverlay


@admin.register(ArtworkOverlay)
class ArtworkOverlayAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image_preview', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Preview'


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'end_date', 'is_closed', 'artwork')
    list_filter = ('is_closed',)
    search_fields = ('name',)
    date_hierarchy = 'date'
    fieldsets = (
        (None, {
            'fields': ('name', ('date', 'end_date'), 'is_closed')
        }),
        ('Artwork', {
            'fields': ('artwork',),
            'description': 'Select an uploaded artwork to use for this holiday.'
        }),
    )


@admin.register(CalendarGeneration)
class CalendarGenerationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_at')
    list_filter = ('room_type', 'month', 'year')
    readonly_fields = ('pdf_file',)
