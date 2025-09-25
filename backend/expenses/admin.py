from django.contrib import admin
from .models import Category, Expense, Bill, UserProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'amount', 'transaction_type', 'category', 'date']
    list_filter = ['transaction_type', 'category', 'date', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    ordering = ['-date', '-created_at']
    date_hierarchy = 'date'


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'amount', 'due_date', 'status', 'frequency']
    list_filter = ['status', 'frequency', 'is_recurring', 'due_date']
    search_fields = ['title', 'description', 'user__username']
    ordering = ['due_date']
    date_hierarchy = 'due_date'
    
    actions = ['mark_as_paid']
    
    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid')
        self.message_user(request, f"{queryset.count()} factures marquées comme payées.")
    mark_as_paid.short_description = "Marquer comme payées"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'monthly_budget', 'currency', 'created_at']
    list_filter = ['currency', 'created_at']
    search_fields = ['user__username', 'user__email']
    ordering = ['user__username']
