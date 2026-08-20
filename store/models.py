from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    title       = models.CharField(max_length=200)
    author      = models.CharField(max_length=200)
    price       = models.DecimalField(max_digits=8, decimal_places=2)
    category    = models.CharField(max_length=100)
    description = models.TextField()
    image       = models.ImageField(upload_to='book_covers/')

    def __str__(self):
        return self.title

class CartItem(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE)
    book     = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

class Order(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    subtotal   = models.DecimalField(max_digits=10, decimal_places=2)
    gst        = models.DecimalField(max_digits=10, decimal_places=2)
    shipping   = models.DecimalField(max_digits=10, decimal_places=2)
    total      = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book     = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price    = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"