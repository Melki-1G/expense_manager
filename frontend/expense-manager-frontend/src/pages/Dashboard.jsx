import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { expenseService, billService } from '../lib/api';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { CreditCard, Receipt, TrendingUp, TrendingDown, Calendar, Plus } from 'lucide-react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [upcomingBills, setUpcomingBills] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [summaryResponse, billsResponse] = await Promise.all([
        expenseService.getSummary(),
        billService.getUpcoming()
      ]);
      
      setSummary(summaryResponse.data);
      setUpcomingBills(billsResponse.data);
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Tableau de bord</h1>
        <div className="flex space-x-2">
          <Button asChild>
            <Link to="/expenses/new">
              <Plus className="mr-2 h-4 w-4" />
              Nouvelle dépense
            </Link>
          </Button>
        </div>
      </div>

      {/* Cartes de résumé */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Dépenses totales</CardTitle>
            <TrendingDown className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              -{summary?.total_expenses || 0}€
            </div>
            <p className="text-xs text-muted-foreground">
              Ce mois-ci
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Revenus totaux</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              +{summary?.total_income || 0}€
            </div>
            <p className="text-xs text-muted-foreground">
              Ce mois-ci
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Solde net</CardTitle>
            <CreditCard className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${
              (summary?.net_amount || 0) >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {(summary?.net_amount || 0) >= 0 ? '+' : ''}{summary?.net_amount || 0}€
            </div>
            <p className="text-xs text-muted-foreground">
              Différence revenus - dépenses
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Graphique des dépenses par catégorie */}
        <Card>
          <CardHeader>
            <CardTitle>Dépenses par catégorie</CardTitle>
            <CardDescription>
              Répartition de vos dépenses par catégorie
            </CardDescription>
          </CardHeader>
          <CardContent>
            {summary?.expenses_by_category?.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={summary.expenses_by_category}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ category, percent }) => `${category} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="amount"
                  >
                    {summary.expenses_by_category.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color || COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `${value}€`} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-64 text-gray-500">
                Aucune dépense à afficher
              </div>
            )}
          </CardContent>
        </Card>

        {/* Tendance mensuelle */}
        <Card>
          <CardHeader>
            <CardTitle>Tendance mensuelle</CardTitle>
            <CardDescription>
              Évolution de vos finances sur les 6 derniers mois
            </CardDescription>
          </CardHeader>
          <CardContent>
            {summary?.monthly_trend?.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={summary.monthly_trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value) => `${value}€`} />
                  <Legend />
                  <Bar dataKey="income" fill="#10B981" name="Revenus" />
                  <Bar dataKey="expenses" fill="#EF4444" name="Dépenses" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-64 text-gray-500">
                Aucune donnée à afficher
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Factures à venir */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Calendar className="mr-2 h-5 w-5" />
            Factures à venir
          </CardTitle>
          <CardDescription>
            Factures à payer dans les 30 prochains jours
          </CardDescription>
        </CardHeader>
        <CardContent>
          {upcomingBills.length > 0 ? (
            <div className="space-y-4">
              {upcomingBills.slice(0, 5).map((bill) => (
                <div key={bill.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-4">
                    <Receipt className="h-8 w-8 text-gray-400" />
                    <div>
                      <p className="font-medium">{bill.title}</p>
                      <p className="text-sm text-gray-500">
                        Échéance: {new Date(bill.due_date).toLocaleDateString('fr-FR')}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold">{bill.amount}€</p>
                    <p className={`text-sm ${
                      bill.status === 'overdue' ? 'text-red-600' : 'text-yellow-600'
                    }`}>
                      {bill.status === 'overdue' ? 'En retard' : 'En attente'}
                    </p>
                  </div>
                </div>
              ))}
              {upcomingBills.length > 5 && (
                <div className="text-center">
                  <Button variant="outline" asChild>
                    <Link to="/bills">
                      Voir toutes les factures ({upcomingBills.length})
                    </Link>
                  </Button>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              Aucune facture à venir
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;

