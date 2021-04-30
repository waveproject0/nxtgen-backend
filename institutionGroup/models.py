from django.contrib.postgres.fields import ArrayField
from django.db import models
from institution.models import Institution



class InstitutionGroup(models.Model):
	name = models.CharField(max_length=50)
	address = models.CharField(max_length=100)
	geolocation = ArrayField(models.FloatField(), size=2, unique=True)

	def __str__(self):
		return self.name


class GroupInstitutionRelation(models.Model):
	institutional_group = models.ForeignKey('InstitutionGroup', on_delete=models.CASCADE)
	institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

	class Meta:
		unique_together = ("institutional_group", "institution")

	def __str__(self):
		return self.institutional_group.name +"/ "+ self.institution.name