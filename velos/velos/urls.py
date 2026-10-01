"""
URL configuration for velos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path
from high_level import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("pays/<int:pk>", views.PaysDetailView.as_view(), name="pays"),
    path("ville/<int:pk>", views.VilleDetailView.as_view(), name="ville"),
    path("lieu/<int:pk>", views.LieuDetailView.as_view(), name="lieu"),
    path("machine/<int:pk>", views.MachineDetailView.as_view(), name="machine"),
    path(
        "quantite_machine/<int:pk>",
        views.QuantiteMachineDetailView.as_view(),
        name="quantite_machine",
    ),
    path("operation/<int:pk>", views.OperationDetailView.as_view(), name="operation"),
    path("produit/<int:pk>", views.ProduitDetailView.as_view(), name="produit"),
    path(
        "quantite_produit/<int:pk>",
        views.QuantiteProduitDetailView.as_view(),
        name="quantite_produit",
    ),
    path("stock/<int:pk>", views.StockDetailView.as_view(), name="stock"),
    path(
        "fournisseur/<int:pk>",
        views.FournisseurDetailView.as_view(),
        name="fournisseur",
    ),
    path(
        "prix_produit/<int:pk>",
        views.PrixProduitDetailView.as_view(),
        name="prix_produit",
    ),
    path("transport/<int:pk>", views.TransportDetailView.as_view(), name="transport"),
    path(
        "point_de_vente/<int:pk>",
        views.PointDeVenteDetailView.as_view(),
        name="point_de_vente",
    ),
    path("facture/<int:pk>", views.FactureDetailView.as_view(), name="facture"),
]
