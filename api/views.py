from django.shortcuts import render
from .models import User, Product, Order, OrderItem, Category, Review, Coupon
from .serializers import UserSerializer, ProductSerializer, OrderSerializer, OrderItemSerializer, CategorySerializer, ReviewSerializer, CouponSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdmin
from django.utils import timezone
# Create your views here.

# ---------------------- SIGNUP FUNCTION ---------------------------
@api_view(['POST'])
def signup(request):
    data = request.data

    if data['password'] != data['confirm_password']:
        return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=data['email']).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=data['email'],
        email=data['email'],
        password=data['password'],
        first_name=data['first_name'],
        role=data.get('role', 'Customer')
    )
    return Response({
        'message': 'Account created successfully',
        'user':{
            'id': user.id,
            'first_name': user.first_name,
            'email': user.email,
            'role': user.role
        }
    }, status=status.HTTP_201_CREATED)

# ---------------------- LOGIN FUNCTION ---------------------------
@api_view(['POST'])
def login(request):
    email=request.data.get('email') 
    password=request.data.get('password')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(username=user.username, password=password)
    if user is None:
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)

    return Response({
        'message': 'Login successful',
        'token': str(refresh.access_token),
        'user': {
            'id': user.id,
            'full_name': user.first_name,
            'email': user.email,
            'role': user.role
        }
    })

# ---------------------- CATEGORY FUNCTIONS ---------------------------

# ---------------------- CATEGORY USER FUNCTIONS ---------------------------
@api_view(['GET'])
def category_browse(request):
    category = Category.objects.all()
    serializer = CategorySerializer(category, many=True)
    return Response(serializer.data)


# ---------------------- CATEGORY ADMIN FUNCTIONS ---------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def category_list(request):

    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def category_details(request, pk):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({'error': 'This category does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        category.delete()
        return Response({'message': 'The Category has been successfully deleted'}, status=status.HTTP_200_OK)


# ---------------------- BROWSE FUNCTION ---------------------------
@api_view(['GET'])
def browse(request):
    category_id = request.GET.get('category')

    if category_id:
        products = Product.objects.filter(category=category_id)
    else:
        products = Product.objects.all()

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


# ---------------------- PLACE ORDER FUNCTION ---------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    order = Order.objects.create(user=request.user)
    total = 0
    coupon_message = None
    items = request.data['items'] # items is a list of dictionaries because one order can contain multiple products. 
    coupon_code = request.data.get('coupon_code')
    for item in items:
        product_id = item['product_id']
        quantity = item['quantity']

        try:
            product_row = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        if product_row.stock >= quantity:
            product_row.stock -= quantity
            product_row.save()
        else:
            return Response({'error': f'Only {product_row.stock} {product_row.name} remain'}, status=status.HTTP_400_BAD_REQUEST)

        orderitem = OrderItem.objects.create(
            order=order,
            product_id=product_id,
            quantity=quantity,
            price_at_purchase=product_row.price,
        )
        total += product_row.price * quantity
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.expiry_date < timezone.now():
                coupon_message = 'Coupon code has expired, full price charged'
            else:
                discount_amount = total * (coupon.discount_percentage / 100)
                total = total - discount_amount
                coupon_message = f'{coupon.discount_percentage}% discount applied'
                order.total = total
        except Coupon.DoesNotExist:
            coupon_message = 'Coupon code is invalid, full price charged'

    order.save()
    return Response({
        'message': 'Order Successfully placed',
        'order_id': order.id,
        'total': order.total,
        'coupon_message': coupon_message
        }, status=status.HTTP_201_CREATED)

# ---------------------- VIEW ORDER FUNCTION ---------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_order(request):
    order = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(order, many=True)
    return Response(serializer.data)

# ---------------------- MODIFY ORDER FUNCTION ---------------------------
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdmin])
def modify_order(request, pk):
    try:
        specific_order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({'error': 'This order does not exist'}, status=status.HTTP_404_NOT_FOUND)

    serializer = OrderSerializer(specific_order, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------------------- PRODUCT FUNCTIONS ---------------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def product_list(request):
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def product_details(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'error': 'This Product does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        product.delete()
        return Response({'message': 'Product has been successfully deleted'}, status=status.HTTP_200_OK)

# ---------------------- REVIEW FUNCTIONS ---------------------------

# ---------------------- CREATE REVIEW FUNCTIONS ---------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request):
    data = request.data
    product_id = data['product_id']

    try:
        product_row = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product does not exist'}, status=status.HTTP_404_NOT_FOUND)

    review = Review.objects.create(
        user=request.user,
        product_id=product_id,
        rating=data['rating'],
        comment=data['comment']
    )

    return Response({
        'message': 'Review successfully created'
    }, status=status.HTTP_201_CREATED)

# ---------------------- VIEW REVIEW FUNCTION ---------------------------
@api_view(['GET'])
def view_review(request):
    product_id = request.GET.get('product')

    if product_id:
        review = Review.objects.filter(product=product_id)
    else:
        review = Review.objects.all()

    serializer = ReviewSerializer(review, many=True)
    return Response(serializer.data)


# ---------------------- COUPON FUNCTIONS ---------------------------

# ---------------------- USER FUNCTIONS ---------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def coupon_browse(request):
    coupon = Coupon.objects.all()
    serializer = CouponSerializer(coupon, many=True)
    return Response(serializer.data)

# ---------------------- ADMIN FUNCTIONS ---------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def coupon_list(request):
    serializer = CouponSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])  
def coupon_details(request, pk):
    try:
        coupon = Coupon.objects.get(pk=pk)
    except Coupon.DoesNotExist:
        return Response({'error': 'This coupon does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = CouponSerializer(coupon, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        coupon.delete()
        return Response({'message': 'The coupon has been successfully deleted'}, status=status.HTTP_200_OK)