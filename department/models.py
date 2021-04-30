from django.db import models
from institution.models import Institution, InstitutionTeacherRelation
from teacherProfile.models import TeacherProfile

class Department(models.Model):
	name = models.CharField(max_length=50)
	institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
	hod = models.ForeignKey(InstitutionTeacherRelation, on_delete=models.SET_NULL, null=True, blank=True)

	class Meta:
		unique_together = ("institution", "name")

	def __str__(self):
		return self.institution.name +" / "+ self.name