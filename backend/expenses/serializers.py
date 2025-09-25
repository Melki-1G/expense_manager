from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Expense, Bill, UserProfile


class UserSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les utilisateurs"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les profils utilisateur"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'monthly_budget', 'currency', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    """Sérialiseur pour les catégories"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'color', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_color(self, value):
        """Valider que la couleur est au format hexadécimal"""
        if not value.startswith('#') or len(value) != 7:
            raise serializers.ValidationError("La couleur doit être au format hexadécimal (#RRGGBB)")
        return value


class ExpenseSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les dépenses"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id', 'title', 'description', 'amount', 'transaction_type', 
            'category', 'category_name', 'category_color', 'date', 'receipt',
            'user', 'user_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'user_username', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Créer une nouvelle dépense en associant l'utilisateur connecté"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BillSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les factures"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Bill
        fields = [
            'id', 'title', 'description', 'amount', 'category', 'category_name', 
            'category_color', 'due_date', 'frequency', 'status', 'is_recurring',
            'user', 'user_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'user_username', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Créer une nouvelle facture en associant l'utilisateur connecté"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ExpenseSummarySerializer(serializers.Serializer):
    """Sérialiseur pour les résumés de dépenses"""
    total_expenses = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_income = serializers.DecimalField(max_digits=10, decimal_places=2)
    net_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    expenses_by_category = serializers.ListField(child=serializers.DictField())
    monthly_trend = serializers.ListField(child=serializers.DictField())


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'inscription des utilisateurs"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate(self, attrs):
        """Valider que les mots de passe correspondent"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs

    def create(self, validated_data):
        """Créer un nouvel utilisateur avec un profil"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user

