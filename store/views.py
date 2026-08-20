from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Book
from .serializers import BookSerializer
from .models import CartItem, Order, OrderItem
from decimal import Decimal

# Returns all books from database
class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

# Creates a new user account
class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email    = request.data.get('email')
        password = request.data.get('password')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already taken'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the user — Django hashes the password automatically
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create a token for this user
        token = Token.objects.create(user=user)

        return Response({
            'token': token.key,
            'username': user.username
        }, status=status.HTTP_201_CREATED)

# Logs in an existing user
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # authenticate() checks username + password against database
        user = authenticate(username=username, password=password)

        if not user:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or create token for this user
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'username': user.username
        })

from rest_framework.permissions import IsAuthenticated
from .models import CartItem

# Get all cart items for logged in user
class CartListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = CartItem.objects.filter(user=request.user)
        data = []
        for item in items:
            data.append({
                'id': item.id,
                'book_id': item.book.id,
                'title': item.book.title,
                'author': item.book.author,
                'price': str(item.book.price),
                'image': request.build_absolute_uri(item.book.image.url),
                'quantity': item.quantity
            })
        return Response(data)

# Add a book to cart
class CartAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        book_id  = request.data.get('book_id')
        quantity = request.data.get('quantity', 1)

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response(
                {'error': 'Book not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # If item already in cart, increase quantity
        item, created = CartItem.objects.get_or_create(
            user=request.user,
            book=book
        )
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()

        return Response({'message': 'Added to cart'})

# Remove a book from cart
class CartRemoveView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id, user=request.user)
            item.delete()
            return Response({'message': 'Removed from cart'})
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Item not found'},
                status=status.HTTP_404_NOT_FOUND
            )

# Update quantity of a cart item
class CartUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        quantity = request.data.get('quantity')
        try:
            item = CartItem.objects.get(id=item_id, user=request.user)
            if quantity <= 0:
                item.delete()
            else:
                item.quantity = quantity
                item.save()
            return Response({'message': 'Cart updated'})
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Item not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get all cart items for this user
        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items:
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate totals
        subtotal = sum(item.book.price * item.quantity for item in cart_items)
        gst      = (subtotal * Decimal('0.18')).quantize(Decimal('0.01'))
        shipping = Decimal('50.00')
        total    = subtotal + gst + shipping

        # Create the order
        order = Order.objects.create(
            user     = request.user,
            subtotal = subtotal,
            gst      = gst,
            shipping = shipping,
            total    = total
        )

        # Create one OrderItem per cart item
        for item in cart_items:
            OrderItem.objects.create(
                order    = order,
                book     = item.book,
                quantity = item.quantity,
                price    = item.book.price
            )

        # Clear the cart after order is placed
        cart_items.delete()

        return Response({
            'message': 'Order placed successfully',
            'order_id': order.id,
            'total': str(total)
        }, status=status.HTTP_201_CREATED)


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        data = []
        for order in orders:
            items = []
            for item in order.items.all():
                items.append({
                    'title'   : item.book.title,
                    'quantity': item.quantity,
                    'price'   : str(item.price)
                })
            data.append({
                'order_id'  : order.id,
                'created_at': order.created_at,
                'subtotal'  : str(order.subtotal),
                'gst'       : str(order.gst),
                'shipping'  : str(order.shipping),
                'total'     : str(order.total),
                'items'     : items
            })
        return Response(data)