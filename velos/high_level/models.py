from django.db import models


class Pays(models.Model):
    nom = models.CharField(max_length=100)
    tva = models.IntegerField()
    tarif_electrique = models.FloatField()  # €/kWh, ex. 0.2
    salaire_minimum = models.IntegerField()  # €/h

    def __str__(self):
        return self.nom

    def json(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "tva": self.tva,
            "tarif_electrique": self.tarif_electrique,
            "salaire_minimum": self.salaire_minimum,
        }


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

    def json(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "taxe_immobiliere": self.taxe_immobiliere,
            "prix_m2": self.prix_m2,
            "pays": self.pays.json() if self.pays else None,
        }


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

    def json(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "ville": self.ville.json() if self.ville else None,
            "superficie": self.superficie,
            "quantite_machines": [qm.json() for qm in self.quantite_machines.all()],
            "consommation_electrique": self.consommation_electrique,
        }


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

    def json(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "prix": self.prix,
            "duree_de_vie": self.duree_de_vie,
            "cout_maintenance": self.cout_maintenance,
            "superficie": self.superficie,
        }


class QuantiteMachine(models.Model):
    machine = models.ForeignKey(
        Machine, on_delete=models.PROTECT, blank=True, null=True
    )
    nombre = models.IntegerField()

    def __str__(self):
        return f"{self.machine} ({self.nombre})"

    def costs(self):
        return self.nombre * self.machine.costs()

    def json(self):
        return {
            "id": self.id,
            "machine": self.machine.json() if self.machine else None,
            "nombre": self.nombre,
        }


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

    def json(self):
        return {
            "id": self.id,
            "nom": self.nom,
            # juste l'id : une chaîne d'opérations pourrait boucler sur elle-même
            "operation_suivante": self.operation_suivante_id,
            "cout": self.cout,
            "machine": self.machine.json() if self.machine else None,
            "quantite_produits": [qp.json() for qp in self.quantite_produits.all()],
            "heures_de_travail": self.heures_de_travail,
            "consommation_electrique": self.consommation_electrique,
        }


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

    def json(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "prix_de_vente": self.prix_de_vente,
            "duree_de_vie": self.duree_de_vie,
            "nombre_par_palette": self.nombre_par_palette,
            # juste les id : Operation.json() contient des produits,
            # qui contiendraient leurs opérations… => boucle infinie
            "operations": [op.id for op in self.operations.all()],
        }


class QuantiteProduit(models.Model):
    produit = models.ForeignKey(
        Produit, on_delete=models.PROTECT, blank=True, null=True
    )
    nombre = models.IntegerField()  # nombre d'unités

    def __str__(self):
        return f"{self.produit} ({self.nombre})"

    def costs(self):
        return self.nombre * self.produit.prix_de_vente

    def json(self):
        return {
            "id": self.id,
            "produit": self.produit.json() if self.produit else None,
            "nombre": self.nombre,
        }


class Stock(models.Model):
    quantite_produits = models.ManyToManyField(QuantiteProduit)
    palettes_max = models.IntegerField()

    def __str__(self):
        return f"Stock {self.id}"

    def costs(self):
        return sum(qp.costs() for qp in self.quantite_produits.all())

    def json(self):
        return {
            "id": self.id,
            "quantite_produits": [qp.json() for qp in self.quantite_produits.all()],
            "palettes_max": self.palettes_max,
        }


class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    prix_produits = models.ManyToManyField("PrixProduit")

    def __str__(self):
        return self.nom

    def json(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "prix_produits": [pp.json() for pp in self.prix_produits.all()],
        }


class PrixProduit(models.Model):
    produit = models.ForeignKey(
        Produit, on_delete=models.PROTECT, blank=True, null=True
    )
    prix_achat = models.IntegerField()

    def __str__(self):
        return f"{self.produit} - {self.prix_achat}"

    def json(self):
        return {
            "id": self.id,
            "produit": self.produit.json() if self.produit else None,
            "prix_achat": self.prix_achat,
        }


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

    def json(self):
        return {
            "id": self.id,
            "nombre_palettes": self.nombre_palettes,
            "cout": self.cout,
            "delai": self.delai,
            "depart": self.depart.json() if self.depart else None,
            "arrivee": self.arrivee.json() if self.arrivee else None,
        }


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

    def json(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "lieu": self.lieu.json(),
            "heures_de_travail": self.heures_de_travail,
            "stock": self.stock.json(),
        }


class Facture(models.Model):
    quantite_produits = models.ManyToManyField(QuantiteProduit)

    reduction = models.IntegerField()

    point_de_vente = models.ForeignKey(PointDeVente, on_delete=models.PROTECT)

    client = models.CharField(max_length=100)

    def __str__(self):
        return f"Facture {self.id}"

    def json(self):
        return {
            "id": self.id,
            "quantite_produits": [qp.json() for qp in self.quantite_produits.all()],
            "reduction": self.reduction,
            "point_de_vente": self.point_de_vente.json(),
            "client": self.client,
        }
