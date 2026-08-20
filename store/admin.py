from django.contrib import admin
from .models import Book, CartItem, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'get_user', 'book', 'quantity', 'price']
    
    def get_user(self, obj):
        return obj.order.user.username
    get_user.short_description = 'User'

class OrderAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'total', 'created_at']
    list_filter   = ['created_at', 'user']
    search_fields = ['user__username']
    inlines       = [OrderItemInline]

admin.site.register(Book)
admin.site.register(CartItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)