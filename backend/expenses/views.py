from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Category, Expense, Bill, UserProfile
from .serializers import (
    CategorySerializer, ExpenseSerializer, BillSerializer, 
    UserProfileSerializer, ExpenseSummarySerializer, UserRegistrationSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet pour les catégories"""
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.all()


class ExpenseViewSet(viewsets.ModelViewSet):
    """ViewSet pour les dépenses"""
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Obtenir un résumé des dépenses de l'utilisateur"""
        user = request.user
        
        # Filtrer par période si spécifiée
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = Expense.objects.filter(user=user)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Calculer les totaux
        expenses = queryset.filter(transaction_type='expense')
        income = queryset.filter(transaction_type='income')
        
        total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_income = income.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        net_amount = total_income - total_expenses
        
        # Dépenses par catégorie
        expenses_by_category = []
        categories = Category.objects.all()
        for category in categories:
            category_expenses = expenses.filter(category=category).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            if category_expenses > 0:
                expenses_by_category.append({
                    'category': category.name,
                    'color': category.color,
                    'amount': category_expenses
                })
        
        # Tendance mensuelle (6 derniers mois)
        monthly_trend = []
        for i in range(6):
            month_start = (timezone.now() - timedelta(days=30*i)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            month_expenses = expenses.filter(date__range=[month_start, month_end]).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            month_income = income.filter(date__range=[month_start, month_end]).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            monthly_trend.append({
                'month': month_start.strftime('%Y-%m'),
                'expenses': month_expenses,
                'income': month_income,
                'net': month_income - month_expenses
            })
        
        summary_data = {
            'total_expenses': total_expenses,
            'total_income': total_income,
            'net_amount': net_amount,
            'expenses_by_category': expenses_by_category,
            'monthly_trend': monthly_trend
        }
        
        serializer = ExpenseSummarySerializer(summary_data)
        return Response(serializer.data)


class BillViewSet(viewsets.ModelViewSet):
    """ViewSet pour les factures"""
    serializer_class = BillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Bill.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Obtenir les factures à venir dans les 30 prochains jours"""
        user = request.user
        today = timezone.now().date()
        upcoming_date = today + timedelta(days=30)
        
        upcoming_bills = Bill.objects.filter(
            user=user,
            due_date__range=[today, upcoming_date],
            status__in=['pending', 'overdue']
        )
        
        serializer = self.get_serializer(upcoming_bills, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Marquer une facture comme payée"""
        bill = self.get_object()
        bill.status = 'paid'
        bill.save()
        
        # Créer une dépense correspondante
        Expense.objects.create(
            user=bill.user,
            title=f"Paiement: {bill.title}",
            description=bill.description,
            amount=bill.amount,
            transaction_type='expense',
            category=bill.category,
            date=timezone.now().date()
        )
        
        serializer = self.get_serializer(bill)
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet pour les profils utilisateur"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def get_object(self):
        """Obtenir ou créer le profil de l'utilisateur connecté"""
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """Inscription d'un nouvel utilisateur"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    """Connexion d'un utilisateur"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'token': token.key
            })
        else:
            return Response({
                'error': 'Nom d\'utilisateur ou mot de passe incorrect'
            }, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({
            'error': 'Nom d\'utilisateur et mot de passe requis'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    """Déconnexion d'un utilisateur"""
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Déconnexion réussie'})
    except:
        return Response({'error': 'Erreur lors de la déconnexion'}, status=status.HTTP_400_BAD_REQUEST)
