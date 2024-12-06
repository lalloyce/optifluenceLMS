from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, ListView
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.views import BaseListView

from .models import STKTransaction
from .services import MPesaSTKService

class STKPushView(LoginRequiredMixin, TemplateView):
    """View for initiating STK Push."""
    template_name = 'mpesastk/stk_push.html'
    
    def get_context_data(self, **kwargs):
        """Add extra context."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'MPesa Payment'
        return context

class STKTransactionListView(BaseListView):
    """List all STK transactions."""
    model = STKTransaction
    template_name = 'mpesastk/transaction_list.html'
    context_object_name = 'transactions'
    title = 'MPesa Transactions'
    search_fields = ['phone_number', 'reference', 'merchant_request_id']

@method_decorator(csrf_exempt, name='dispatch')
class STKPushAPIView(TemplateView):
    """API view for STK Push operations."""
    
    def post(self, request, *args, **kwargs):
        """Handle STK Push initiation."""
        try:
            data = json.loads(request.body)
            phone = data.get('phone')
            amount = data.get('amount')
            reference = data.get('reference', 'Payment')
            description = data.get('description', 'Payment for services')
            
            if not all([phone, amount]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Phone and amount are required'
                }, status=400)
            
            service = MPesaSTKService()
            transaction = service.initiate_stk_push(
                phone_number=phone,
                amount=amount,
                reference=reference,
                description=description
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'STK push initiated successfully',
                'data': {
                    'merchant_request_id': transaction.merchant_request_id,
                    'checkout_request_id': transaction.checkout_request_id
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class STKCallbackView(TemplateView):
    """Handle MPesa STK Push callbacks."""
    
    def post(self, request, *args, **kwargs):
        """Process callback data."""
        try:
            callback_data = json.loads(request.body)
            
            service = MPesaSTKService()
            transaction = service.process_callback(callback_data)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Callback processed successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

class STKQueryView(LoginRequiredMixin, TemplateView):
    """View for querying STK Push status."""
    
    def post(self, request, *args, **kwargs):
        """Query STK Push status."""
        try:
            checkout_request_id = request.POST.get('checkout_request_id')
            
            if not checkout_request_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Checkout request ID is required'
                }, status=400)
            
            service = MPesaSTKService()
            result = service.query_stk_status(checkout_request_id)
            
            return JsonResponse({
                'status': 'success',
                'data': result
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
