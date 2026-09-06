from django.shortcuts import render
from .models import User, Product, Order, OrderItem
from .serializers import UserSerializer, ProductSerializer, OrderSerializer, OrderItemSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdmin
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

# ---------------------- BROWSE FUNCTION ---------------------------
@api_view(['GET'])
def browse(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


# ---------------------- PLACE ORDER FUNCTION ---------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    order = Order.objects.create(user=request.user)
    items = request.data['items']
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
    return Response({
        'message': 'Order Successfully placed',
        'order_id': order.id,
        }, status=status.HTTP_201_CREATED)

# ---------------------- VIEW ORDER FUNCTION ---------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_order(request):
    order = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(order, many=True)
    return Response(serializer.data)


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
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        product.delete()
        return Response({'message': 'Product has been successfully deleted'}, status=status.HTTP_200_OK)