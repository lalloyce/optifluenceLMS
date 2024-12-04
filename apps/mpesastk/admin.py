"""MPesa STK Push admin interface."""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import STKTransaction
from .services import MPesaSTKService

@admin.register(STKTransaction)
class STKTransactionAdmin(admin.ModelAdmin):
    """Admin interface for STK transactions."""
    
    list_display = (
        'reference',
        'phone_number',
        'amount',
        'status_badge',
        'created_at',
        'actions_buttons'
    )
    list_filter = ('status', 'created_at')
    search_fields = (
        'phone_number',
        'reference',
        'merchant_request_id',
        'checkout_request_id'
    )
    readonly_fields = (
        'merchant_request_id',
        'checkout_request_id',
        'result_code',
        'result_desc',
        'created_at',
        'updated_at'
    )
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Transaction Details', {
            'fields': (
                'reference',
                'description',
                'amount',
                'phone_number',
                'status'
            )
        }),
        ('MPesa Response', {
            'fields': (
                'merchant_request_id',
                'checkout_request_id',
                'result_code',
                'result_desc'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'pending': 'warning',
            'successful': 'success',
            'failed': 'danger'
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors.get(obj.status, 'secondary'),
            obj.status.title()
        )
    status_badge.short_description = 'Status'
    
    def actions_buttons(self, obj):
        """Display action buttons."""
        buttons = []
        
        # Query status button for pending transactions
        if obj.status == 'pending':
            buttons.append(
                format_html(
                    '<button onclick="queryStatus(\'{}\', \'{}\')" '
                    'class="btn btn-info btn-sm">'
                    '<i class="fas fa-sync"></i> Query Status'
                    '</button>',
                    obj.checkout_request_id,
                    reverse('admin:mpesastk_stktransaction_changelist')
                )
            )
        
        # View details button
        buttons.append(
            format_html(
                '<a href="{}" class="btn btn-primary btn-sm">'
                '<i class="fas fa-eye"></i> View Details'
                '</a>',
                reverse('admin:mpesastk_stktransaction_change', args=[obj.pk])
            )
        )
        
        return format_html('&nbsp;'.join(buttons))
    actions_buttons.short_description = 'Actions'
    
    class Media:
        """Add custom CSS and JavaScript."""
        css = {
            'all': (
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
            )
        }
        js = (
            'https://code.jquery.com/jquery-3.6.0.min.js',
            'admin/js/mpesa_admin.js',
        )
    
    def save_model(self, request, obj, form, change):
        """Override save to handle status changes."""
        if change and 'status' in form.changed_data:
            obj.save()
            self.message_user(
                request,
                f'Transaction status updated to {obj.status}'
            )
        else:
            super().save_model(request, obj, form, change)
