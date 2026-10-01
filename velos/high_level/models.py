from django.db import models


class Pays(models.Model):
    nom = models.CharField(max_length=100)
    tva = models.IntegerField()
    tarif_electrique = models.FloatField()  # €/kWh, ex. 0.2
    salaire_minimum = models.IntegerField()  # €/h

    def __str__(self):
        return self.nom


class Ville(models.Model):
    nom = models.CharField(max_length=100)
    taxe_immobiliere = models.IntegerField()
    prix_m2 = models.IntegerField()
    pays = models.ForeignKey(Pays, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return self.nom

    def costs(self):
        # coût de tous les lieux situés dans la ville
        return sum(lieu.costs() for lieu in self.lieu_set.all())


class Lieu(models.Model):
    nom = models.CharField(max_length=100)
    ville = models.ForeignKey(Ville, on_delete=models.PROTECT, blank=True, null=True)
    superficie = models.IntegerField()
    quantite_machines = models.ManyToManyField("QuantiteMachine")
    consommation_electrique = models.IntegerField()

    def __str__(self):
        return self.nom

    def costs(self):
        terrain = self.superficie * self.ville.prix_m2
        electricite = self.consommation_electrique * self.ville.pays.tarif_electrique
        machines = sum(qm.costs() for qm in self.quantite_machines.all())
        # le stock est rattaché aux points de vente de ce lieu
        points_de_vente = sum(pdv.costs() for pdv in self.pointdevente_set.all())
        return terrain + electricite + machines + points_de_vente


class Machine(models.Model):
    nom = models.CharField(max_length=100)
    prix = models.IntegerField()
    duree_de_vie = models.IntegerField()
    cout_maintenance = models.IntegerField()
    superficie = models.IntegerField()

    def __str__(self):
        return self.nom

    def costs(self):
        return self.prix


class QuantiteMachine(models.Model):
    machine = models.ForeignKey(
        Machine, on_delete=models.PROTECT, blank=True, null=True
    )
    nombre = models.IntegerField()

    def __str__(self):
        return f"{self.machine} ({self.nombre})"

    def costs(self):
        return self.nombre * self.machine.costs()


class Operation(models.Model):
    nom = models.CharField(max_length=100)

    operation_suivante = models.ForeignKey(
        "self", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )

    cout = models.IntegerField()

    machine = models.ForeignKey(
        Machine, on_delete=models.PROTECT, blank=True, null=True
    )

    quantite_produits = models.ManyToManyField("QuantiteProduit", blank=True)

    heures_de_travail = models.IntegerField()
    consommation_electrique = models.IntegerField()

    def __str__(self):
        return self.nom

    def costs(self):
        # coût propre de l'opération + matières consommées
        return self.cout + sum(qp.costs() for qp in self.quantite_produits.all())


class Produit(models.Model):
    nom = models.CharField(max_length=100)
    prix_de_vente = models.IntegerField()  # prix d'une unité
    duree_de_vie = models.IntegerField()
    nombre_par_palette = models.IntegerField()

    operations = models.ManyToManyField(Operation, blank=True)

    def __str__(self):
        return self.nom

    def costs(self):
        # coût de fabrication = somme des opérations
        return sum(op.costs() for op in self.operations.all())


class QuantiteProduit(models.Model):
    produit = models.ForeignKey(
        Produit, on_delete=models.PROTECT, blank=True, null=True
    )
    nombre = models.IntegerField()  # nombre d'unités

    def __str__(self):
        return f"{self.produit} ({self.nombre})"

    def costs(self):
        return self.nombre * self.produit.prix_de_vente


class Stock(models.Model):
    quantite_produits = models.ManyToManyField(QuantiteProduit)
    palettes_max = models.IntegerField()

    def __str__(self):
        return f"Stock {self.id}"

    def costs(self):
        return sum(qp.costs() for qp in self.quantite_produits.all())


class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    prix_produits = models.ManyToManyField("PrixProduit")

    def __str__(self):
        return self.nom


class PrixProduit(models.Model):
    produit = models.ForeignKey(
        Produit, on_delete=models.PROTECT, blank=True, null=True
    )
    prix_achat = models.IntegerField()

    def __str__(self):
        return f"{self.produit} - {self.prix_achat}"


class Transport(models.Model):
    nombre_palettes = models.IntegerField()
    cout = models.IntegerField()  # coût par palette
    delai = models.IntegerField()

    depart = models.ForeignKey(
        Lieu,
        on_delete=models.PROTECT,
        related_name="transports_depart",
        blank=True,
        null=True,
    )

    arrivee = models.ForeignKey(
        Lieu,
        on_delete=models.PROTECT,
        related_name="transports_arrivee",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.depart} -> {self.arrivee}"

    def costs(self):
        return self.nombre_palettes * self.cout


class PointDeVente(models.Model):
    nom = models.CharField(max_length=100)

    lieu = models.ForeignKey(Lieu, on_delete=models.PROTECT)

    heures_de_travail = models.IntegerField()

    stock = models.ForeignKey(Stock, on_delete=models.PROTECT)

    def __str__(self):
        return self.nom

    def costs(self):
        salaires = self.heures_de_travail * self.lieu.ville.pays.salaire_minimum
        return salaires + self.stock.costs()


class Facture(models.Model):
    quantite_produits = models.ManyToManyField(QuantiteProduit)

    reduction = models.IntegerField()

    point_de_vente = models.ForeignKey(PointDeVente, on_delete=models.PROTECT)

    client = models.CharField(max_length=100)

    def __str__(self):
        return f"Facture {self.id}"
