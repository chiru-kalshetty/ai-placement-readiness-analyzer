from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html
from django.http import HttpResponse
from django.contrib import messages
import csv
from .models import Student


# ✅ FILTERS
class CGPAFilter(admin.SimpleListFilter):
    title = 'CGPA Range'
    parameter_name = 'cgpa_range'

    def lookups(self, request, model_admin):
        return [
            ('high', 'High (≥8.0)'),
            ('medium', 'Medium (6.0-7.9)'),
            ('low', 'Low (<6.0)'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'high':
            return queryset.filter(cgpa__gte=8.0)
        if self.value() == 'medium':
            return queryset.filter(cgpa__gte=6.0, cgpa__lt=8.0)
        if self.value() == 'low':
            return queryset.filter(cgpa__lt=6.0)
        return queryset


# ✅ ADMIN PANEL
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        'name', 'email', 'branch',
        'cgpa_colored', 'score_display',
        'level_display', 'projects', 'internships'
    )

    list_editable = ('projects', 'internships')

    search_fields = ['name', 'email']

    list_filter = ('branch', CGPAFilter)

    ordering = ['-cgpa']

    list_per_page = 25

    readonly_fields = ('score_display', 'level_display')

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'email', 'branch')
        }),
        ('Academic', {
            'fields': ('cgpa',)
        }),
        ('Experience', {
            'fields': ('projects', 'internships')
        }),
        ('Analysis', {
            'fields': ('score_display', 'level_display')
        }),
    )

    actions = ['export_selected_csv']

    # ✅ CGPA COLOR
    def cgpa_colored(self, obj):
        if obj.cgpa >= 8:
            color = "green"
        elif obj.cgpa >= 6:
            color = "orange"
        else:
            color = "red"

        return format_html('<b style="color:{};">{}</b>', color, obj.cgpa)

    cgpa_colored.short_description = "CGPA"

    # ✅ SCORE
    def score_display(self, obj):
        score = min((obj.cgpa * 10) + (obj.projects * 10) + (obj.internships * 15), 100)
        return f"{score:.1f}"

    score_display.short_description = "Score"

    # ✅ LEVEL
    def level_display(self, obj):
        score = min((obj.cgpa * 10) + (obj.projects * 10) + (obj.internships * 15), 100)

        if score >= 85:
            text = "🏆 Elite"
            color = "green"
        elif score >= 70:
            text = "🥇 Skilled"
            color = "blue"
        elif score >= 50:
            text = "🥈 Beginner"
            color = "orange"
        else:
            text = "❌ Needs Work"
            color = "red"

        return format_html('<b style="color:{};">{}</b>', color, text)

    level_display.short_description = "Level"

    # ✅ EXPORT CSV
    def export_selected_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Branch', 'CGPA', 'Score'])

        for student in queryset:
            score = min((student.cgpa * 10) + (student.projects * 10) + (student.internships * 15), 100)

            writer.writerow([
                student.name,
                student.email,
                student.branch,
                student.cgpa,
                score
            ])

        self.message_user(request, "Export successful", messages.SUCCESS)
        return response

    export_selected_csv.short_description = "Export Selected as CSV"