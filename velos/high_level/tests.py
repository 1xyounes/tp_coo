from django.test import TestCase

from .models import (
    Lieu,
    Machine,
    Pays,
    PointDeVente,
    Produit,
    QuantiteMachine,
    QuantiteProduit,
    Stock,
    Ville,
)


class MachineModelTests(TestCase):
    def test_machine_creation(self):
        self.assertEqual(Machine.objects.count(), 0)
        Machine.objects.create(
            nom="CNC",
            prix=28_000,
            duree_de_vie=10,
            cout_maintenance=500,
            superficie=5,
        )
        self.assertEqual(Machine.objects.count(), 1)


class CostsTests(TestCase):
    def setUp(self):
        
        france = Pays.objects.create(
            nom="France", tva=20, tarif_electrique=0.2, salaire_minimum=12
        )

        
        labege = Ville.objects.create(
            nom="Labège", taxe_immobiliere=0, prix_m2=2_000, pays=france
        )

       
        m1 = Machine.objects.create(
            nom="Presse", prix=10_000, duree_de_vie=10, cout_maintenance=0, superficie=5
        )
        m2 = Machine.objects.create(
            nom="Scie", prix=5_000, duree_de_vie=10, cout_maintenance=0, superficie=2
        )

        qm1 = QuantiteMachine.objects.create(machine=m1, nombre=1)
        qm2 = QuantiteMachine.objects.create(machine=m2, nombre=1)

   
        l1 = Lieu.objects.create(
            nom="LBG-01", ville=labege, superficie=50, consommation_electrique=5_000
        )
        l1.quantite_machines.add(qm1)
        l1.quantite_machines.add(qm2)
        l1.save()
        p1 = Produit.objects.create(
            nom="Tube d'acier",
            prix_de_vente=10,  
            duree_de_vie=10,
            nombre_par_palette=100,
        )
        p2 = Produit.objects.create(
            nom="Câble",
            prix_de_vente=30,  
            duree_de_vie=10,
            nombre_par_palette=100,
        )
        
        qp1 = QuantiteProduit.objects.create(produit=p1, nombre=200)
        qp2 = QuantiteProduit.objects.create(produit=p2, nombre=100)

        s1 = Stock.objects.create(palettes_max=10)
        s1.quantite_produits.add(qp1)
        s1.quantite_produits.add(qp2)
        s1.save()

        
        PointDeVente.objects.create(
            nom="PDV Labège", lieu=l1, heures_de_travail=0, stock=s1
        )

    def test_stock_costs(self):
        self.assertEqual(Stock.objects.first().costs(), 5_000)

    def test_lieu_costs(self):
        self.assertEqual(Lieu.objects.first().costs(), 121_000)

    def test_ville_costs(self):
        self.assertEqual(Ville.objects.first().costs(), 121_000)
