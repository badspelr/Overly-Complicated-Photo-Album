"""
Category-related views.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from ..forms import CategoryForm
from ..models import Category
from .base_views import CategoryPermissionMixin, get_delete_context, log_user_action


@method_decorator(login_required, name='dispatch')
class CategoryListView(LoginRequiredMixin, ListView):
    """List all categories."""
    model = Category
    template_name = 'album/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Category.objects.all().order_by('name')
        else:
            return Category.objects.filter(created_by=self.request.user).order_by('name')


@method_decorator(login_required, name='dispatch')
class CategoryCreateView(LoginRequiredMixin, CreateView):
    """Create a new category."""
    model = Category
    form_class = CategoryForm
    template_name = 'album/create_category.html'
    success_url = reverse_lazy('album:category_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Category created successfully.')
        log_user_action('category_created', self.request.user, 'category', form.instance.id)
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class CategoryUpdateView(CategoryPermissionMixin, LoginRequiredMixin, UpdateView):
    """Update an existing category."""
    model = Category
    form_class = CategoryForm
    template_name = 'album/create_category.html'
    success_url = reverse_lazy('album:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully.')
        log_user_action('category_updated', self.request.user, 'category', form.instance.id)
        return super().form_valid(form)



@method_decorator(login_required, name='dispatch')
class CategoryDeleteView(CategoryPermissionMixin, LoginRequiredMixin, DeleteView):
    """Delete a category."""
    model = Category
    template_name = 'album/delete_confirmation.html'
    success_url = reverse_lazy('album:category_list')

    def form_valid(self, form):
        category_id = self.object.id
        category_name = self.object.name
        log_user_action('category_deleted', self.request.user, 'category', category_id)
        messages.success(self.request, f'Category "{category_name}" deleted successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_delete_context(self.object, 'Category', 'This will permanently delete the category.'))
        return context
