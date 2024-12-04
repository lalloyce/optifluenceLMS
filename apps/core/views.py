"""Core views and mixins."""
import logging
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction

logger = logging.getLogger(__name__)

class BaseViewMixin:
    """Base mixin for all views."""
    
    def get_context_data(self, **kwargs):
        """Add common context data."""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.get_title(),
            'active_tab': getattr(self, 'active_tab', None),
        })
        return context
    
    def get_title(self):
        """Get page title."""
        return getattr(self, 'title', '')

class BaseListView(LoginRequiredMixin, BaseViewMixin, ListView):
    """Base list view with pagination and search."""
    paginate_by = 10
    search_fields = []
    
    def get_queryset(self):
        """Apply search filter to queryset."""
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        
        if search_query and self.search_fields:
            from django.db.models import Q
            query = Q()
            for field in self.search_fields:
                query |= Q(**{f"{field}__icontains": search_query})
            queryset = queryset.filter(query)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add search query to context."""
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

class BaseModelFormMixin:
    """Base mixin for model form views."""
    
    def form_valid(self, form):
        """Handle valid form."""
        try:
            with transaction.atomic():
                response = super().form_valid(form)
                messages.success(self.request, self.get_success_message())
                logger.info(
                    f"{self.__class__.__name__}: {self.model.__name__} "
                    f"{self.object.pk} saved successfully by user {self.request.user}"
                )
                return response
        except Exception as e:
            messages.error(self.request, f"Error: {str(e)}")
            logger.error(
                f"{self.__class__.__name__}: Error saving {self.model.__name__} "
                f"by user {self.request.user}: {str(e)}"
            )
            return self.form_invalid(form)
    
    def get_success_message(self):
        """Get success message."""
        return f"{self.model.__name__} saved successfully."

class BaseCreateView(LoginRequiredMixin, BaseViewMixin, BaseModelFormMixin, CreateView):
    """Base create view."""
    template_name_suffix = '_form'
    
    def get_title(self):
        """Get page title."""
        return f"Create {self.model._meta.verbose_name}"

class BaseUpdateView(LoginRequiredMixin, BaseViewMixin, BaseModelFormMixin, UpdateView):
    """Base update view."""
    template_name_suffix = '_form'
    
    def get_title(self):
        """Get page title."""
        return f"Edit {self.model._meta.verbose_name}"

class BaseDeleteView(LoginRequiredMixin, BaseViewMixin, DeleteView):
    """Base delete view."""
    template_name = 'core/confirm_delete.html'
    
    def get_title(self):
        """Get page title."""
        return f"Delete {self.model._meta.verbose_name}"
    
    def delete(self, request, *args, **kwargs):
        """Handle deletion."""
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(request, f"{self.model.__name__} deleted successfully.")
            logger.info(
                f"{self.__class__.__name__}: {self.model.__name__} "
                f"{self.object.pk} deleted by user {request.user}"
            )
            return response
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            logger.error(
                f"{self.__class__.__name__}: Error deleting {self.model.__name__} "
                f"{self.object.pk} by user {request.user}: {str(e)}"
            )
            return self.get(request, *args, **kwargs)
