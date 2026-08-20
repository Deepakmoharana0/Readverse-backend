from django.contrib import admin
from django.urls import path
from store.views import (
    BookListView, RegisterView, LoginView,
    CartListView, CartAddView, CartRemoveView, CartUpdateView,
    PlaceOrderView, OrderListView
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/books/', BookListView.as_view()),
    path('api/register/', RegisterView.as_view()),
    path('api/login/', LoginView.as_view()),
    path('api/cart/', CartListView.as_view()),
    path('api/cart/add/', CartAddView.as_view()),
    path('api/cart/remove/<int:item_id>/', CartRemoveView.as_view()),
    path('api/cart/update/<int:item_id>/', CartUpdateView.as_view()),
    path('api/orders/', OrderListView.as_view()),
    path('api/orders/place/', PlaceOrderView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)