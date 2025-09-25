from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    """Modèle pour les catégories de dépenses"""
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#007bff')  # Couleur hexadécimale
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Expense(models.Model):
    """Modèle pour les dépenses"""
    TRANSACTION_TYPES = [
        ('expense', 'Dépense'),
        ('income', 'Revenu'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default='expense')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.amount}€ ({self.get_transaction_type_display()})"


class Bill(models.Model):
    """Modèle pour les factures récurrentes ou ponctuelles"""
    FREQUENCY_CHOICES = [
        ('once', 'Une fois'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('yearly', 'Annuel'),
    ]

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('paid', 'Payée'),
        ('overdue', 'En retard'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bills')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField()
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='once')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_recurring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.amount}€ (Échéance: {self.due_date})"


class UserProfile(models.Model):
    """Modèle pour étendre le profil utilisateur"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    monthly_budget = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(max_length=3, default='EUR')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profil de {self.user.username}"
