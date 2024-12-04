from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from ..models import RiskAlert, Loan
from ..services.risk_alerts import RiskAlertService

class RiskManagerRequired(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name__in=['Risk Managers', 'Loan Officers']).exists()

class RiskDashboardView(LoginRequiredMixin, RiskManagerRequired, TemplateView):
    template_name = 'loans/risk_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get active alerts
        active_alerts = RiskAlert.objects.filter(is_active=True)
        
        # Get alerts summary
        context['alerts_summary'] = RiskAlertService.get_active_alerts_summary()
        
        # Get critical alerts
        context['critical_alerts'] = active_alerts.filter(
            severity=RiskAlert.Severity.CRITICAL
        ).select_related('loan', 'loan__customer').order_by('-created_at')[:5]
        
        # Get high risk loans
        context['high_risk_loans'] = Loan.objects.filter(
            risk_score__lt=40,
            status__in=[Loan.Status.PENDING, Loan.Status.UNDER_REVIEW]
        ).select_related('customer').order_by('risk_score')[:5]
        
        # Get alert trends
        now = timezone.now()
        last_week = now - timedelta(days=7)
        
        trends = RiskAlert.objects.filter(
            created_at__gte=last_week
        ).extra(
            select={'date': 'DATE(created_at)'}
        ).values('date', 'severity').annotate(
            count=Count('id')
        ).order_by('date', 'severity')
        
        context['alert_trends'] = trends
        
        return context

class RiskDashboardDataView(LoginRequiredMixin, RiskManagerRequired, View):
    def get(self, request, *args, **kwargs):
        """Get updated dashboard data for AJAX refresh."""
        
        active_alerts = RiskAlert.objects.filter(is_active=True)
        
        data = {
            'alerts_summary': RiskAlertService.get_active_alerts_summary(),
            'critical_alerts': [
                {
                    'id': alert.id,
                    'type': alert.get_alert_type_display(),
                    'message': alert.message,
                    'loan_ref': alert.loan.reference_number,
                    'customer': alert.loan.customer.full_name,
                    'created_at': alert.created_at.isoformat()
                }
                for alert in active_alerts.filter(
                    severity=RiskAlert.Severity.CRITICAL
                ).select_related('loan', 'loan__customer').order_by('-created_at')[:5]
            ],
            'high_risk_loans': [
                {
                    'id': loan.id,
                    'reference': loan.reference_number,
                    'customer': loan.customer.full_name,
                    'amount': float(loan.amount),
                    'risk_score': loan.risk_score,
                    'status': loan.get_status_display()
                }
                for loan in Loan.objects.filter(
                    risk_score__lt=40,
                    status__in=[Loan.Status.PENDING, Loan.Status.UNDER_REVIEW]
                ).select_related('customer').order_by('risk_score')[:5]
            ]
        }
        
        return JsonResponse(data)
