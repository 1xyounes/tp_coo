from django.http import JsonResponse
from django.views.generic import DetailView

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


class JsonDetailView(DetailView):
    """DetailView qui renvoie l'objet en JSON au lieu d'un template HTML."""

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(
            self.object.json(),
            json_dumps_params={"ensure_ascii": False, "indent": 2},
        )


class PaysDetailView(JsonDetailView):
    model = Pays


class VilleDetailView(JsonDetailView):
    model = Ville


class LieuDetailView(JsonDetailView):
    model = Lieu


class MachineDetailView(JsonDetailView):
    model = Machine


class QuantiteMachineDetailView(JsonDetailView):
    model = QuantiteMachine


class OperationDetailView(JsonDetailView):
    model = Operation


class ProduitDetailView(JsonDetailView):
    model = Produit


class QuantiteProduitDetailView(JsonDetailView):
    model = QuantiteProduit


class StockDetailView(JsonDetailView):
    model = Stock


class FournisseurDetailView(JsonDetailView):
    model = Fournisseur


class PrixProduitDetailView(JsonDetailView):
    model = PrixProduit


class TransportDetailView(JsonDetailView):
    model = Transport


class PointDeVenteDetailView(JsonDetailView):
    model = PointDeVente


class FactureDetailView(JsonDetailView):
    model = Facture# Create your views here.
