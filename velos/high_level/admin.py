# Register your models here.
from django.contrib import admin

from .models import (
    Facture,
    Fournisseur,
    Lieu,
    Machine,
    Operation,
    Pays,
    PointDeVente,
    PrixProduit,
    Produit,
    QuantiteMachine,
    QuantiteProduit,
    Stock,
    Transport,
    Ville,
)

admin.site.register(Pays)
admin.site.register(Ville)
admin.site.register(Lieu)
admin.site.register(Machine)
admin.site.register(QuantiteMachine)
admin.site.register(Operation)
admin.site.register(Produit)
admin.site.register(QuantiteProduit)
admin.site.register(Stock)
admin.site.register(Fournisseur)
admin.site.register(PrixProduit)
admin.site.register(Transport)
admin.site.register(PointDeVente)
admin.site.register(Facture)
