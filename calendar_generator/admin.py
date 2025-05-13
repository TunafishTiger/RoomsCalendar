from django.contrib import admin

from .models import Holiday, CalendarGeneration


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'end_date', 'is_closed', 'artwork_path')
    list_filter = ('is_closed',)
    search_fields = ('name',)
    date_hierarchy = 'date'
    fieldsets = (
        (None, {
            'fields': ('name', ('date', 'end_date'), 'is_closed', 'artwork_path')
        }),
    )


@admin.register(CalendarGeneration)
class CalendarGenerationAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created_at')
    list_filter = ('room_type', 'month', 'year')
    readonly_fields = ('pdf_file',)
