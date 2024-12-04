from django.contrib import admin
from django.utils.html import format_html
from .models.config import LoanConfig

# Register your models here.

@admin.register(LoanConfig)
class LoanConfigAdmin(admin.ModelAdmin):
    list_display = [
        'loan_type',
        'interest_rate_display',
        'term_days_display',
        'penalty_rate_display',
        'effective_period',
        'status'
    ]
    list_filter = ['loan_type', 'effective_from']
    search_fields = ['loan_type']
    readonly_fields = ['created_at', 'created_by', 'updated_at', 'updated_by']
    fieldsets = [
        (None, {
            'fields': ['loan_type']
        }),
        ('Interest Configuration', {
            'fields': ['interest_rate']
        }),
        ('Term Configuration', {
            'fields': ['term_days']
        }),
        ('Penalty Configuration', {
            'fields': ['penalty_rate']
        }),
        ('Validity Period', {
            'fields': ['effective_from', 'effective_to']
        }),
        ('Audit Information', {
            'fields': ['created_at', 'created_by', 'updated_at', 'updated_by'],
            'classes': ['collapse']
        })
    ]

    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def interest_rate_display(self, obj):
        return format_html('{}%', obj.interest_rate)
    interest_rate_display.short_description = 'Interest Rate'

    def term_days_display(self, obj):
        return format_html('{} days', obj.term_days)
    term_days_display.short_description = 'Term'

    def penalty_rate_display(self, obj):
        return format_html('{}% per month', obj.penalty_rate)
    penalty_rate_display.short_description = 'Penalty Rate'

    def effective_period(self, obj):
        if obj.effective_to:
            return format_html(
                '{} to {}',
                obj.effective_from.strftime('%Y-%m-%d'),
                obj.effective_to.strftime('%Y-%m-%d')
            )
        return format_html(
            'From {}',
            obj.effective_from.strftime('%Y-%m-%d')
        )
    effective_period.short_description = 'Effective Period'

    def status(self, obj):
        if not obj.effective_to:
            return format_html(
                '<span style="color: green;">Current</span>'
            )
        return format_html(
            '<span style="color: grey;">Expired</span>'
        )
    status.short_description = 'Status'
