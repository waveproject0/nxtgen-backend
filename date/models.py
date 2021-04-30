from django.db import models
from taggit.managers import TaggableManager
from django.db.models.signals import post_save
from django.contrib.postgres.fields import ArrayField

from announcement.models import InstitutionAnnouncementRelation, DepartmentAnnouncementRelation,\
ClassAnnouncementRelation, SectionAnnouncementRelation, SubjectTeacherAnnouncementRelation,\
AdditionalSubjectTeacherAnnouncementRelation

from institution.models import Institution
from department.models import Department
from Class.models import Class, ClassSectionRelation, ClassSubjectTeacherRelation, AdditionalSubjectTeacherRelation


class Date(models.Model):
	DATE_TYPE = (
			('emergency','Emergency'),
			('event','Event'),
			('holiday','Holiday'),
			('exam','Exam'),
			('industrial visite','Industrial visite'),
			('fest','FEST')
		)

	date = ArrayField(models.DateField(auto_now=False, auto_now_add=False))
	repeat = models.BooleanField(default=False)
	label = models.CharField(max_length=50, choices=DATE_TYPE)
	short_title = models.CharField(max_length=100)

	def __str__(self):
		return str(self.date) +" / "+ self.short_title +" / "+ self.label


class DateInstitutionRelation(models.Model):
	date = models.OneToOneField('Date', on_delete=models.CASCADE)
	institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
	announcement = models.OneToOneField(InstitutionAnnouncementRelation, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return self.institution.name +" / "+ str(self.date.date)


class PublicDateInstitutionRelation(models.Model):
	VISIBILITY_OPTION = (
			('global','Global'),
			('local','Local')
		)

	date_institution = models.OneToOneField('DateInstitutionRelation', on_delete=models.CASCADE)
	visibility = models.CharField(max_length=50, choices=VISIBILITY_OPTION)
	tags = TaggableManager()

	@property
	def get_tags(self):
		return self.tags.all()
	

	def __str__(self):
		return str(self.date_institution.date.date) +" / "+ self.visibility

# public date relation creation signal
def create_public_date_relation(sender, **kwargs):
	if kwargs['created']:
		if hasattr(kwargs['instance'],'_public'):
			if getattr(kwargs['instance'],'_public') == True:
				public_date_obj = PublicDateInstitutionRelation.objects.create(
					date_institution=kwargs['instance'],visibility=kwargs['instance']._visibility_option
					)

				for tag in kwargs['instance']._tags:
					public_date_obj.tags.add(tag)

post_save.connect(create_public_date_relation, sender=DateInstitutionRelation, weak=False)
# signal ends


class DateDepartmentRelation(models.Model):
	date = models.OneToOneField('Date', on_delete=models.CASCADE)
	department = models.ForeignKey(Department, on_delete=models.CASCADE)
	announcement = models.OneToOneField(DepartmentAnnouncementRelation, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return self.institution.name +" / "+ str(self.date.date)



class DateClassRelation(models.Model):
	date = models.OneToOneField('Date', on_delete=models.CASCADE)
	Class = models.ForeignKey(Class, on_delete=models.CASCADE)
	announcement = models.OneToOneField(ClassAnnouncementRelation, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return self.Class.course.name +" / "+ str(self.date.date)


class DateSectionRelation(models.Model):
	date = models.OneToOneField('Date', on_delete=models.CASCADE)
	section = models.ForeignKey(ClassSectionRelation, on_delete=models.CASCADE)
	announcement = models.OneToOneField(SectionAnnouncementRelation, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return self.section.section +" / "+ str(self.date.date)


class DateSubjectTeacherRelation(models.Model):
	date = models.OneToOneField('Date', on_delete=models.CASCADE)
	subject_teacher = models.ForeignKey(ClassSubjectTeacherRelation, on_delete=models.CASCADE)
	announcement = models.OneToOneField(SubjectTeacherAnnouncementRelation, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return self.subject_teacher.subject.name +" / "+ str(self.date.date)


class DateAdditionalSubjectTeacherRelation(models.Model):
	date = models.OneToOneField('Date', on_delete=models.CASCADE)
	additional_subject_teacher = models.ForeignKey(AdditionalSubjectTeacherRelation, on_delete=models.CASCADE)
	announcement = models.OneToOneField(AdditionalSubjectTeacherAnnouncementRelation, on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return self.additional_subject_teacher.subject.name +" / "+ str(self.date.date)






# date relation creation signal
def create_date_relation(sender, **kwargs):
	if kwargs['created']:
		if getattr(kwargs['instance'],'_date_relation_name') == 'institution_date':
			institution_date_obj = DateInstitutionRelation(
			date=kwargs['instance'],institution=kwargs['instance']._authority_relation_obj
			)

			if hasattr(kwargs['instance'], '_announcement_relation_obj'):
				institution_date_obj.announcement = kwargs['instance']._announcement_relation_obj

				if hasattr(kwargs['instance'], '_public'):
					if getattr(kwargs['instance'],'_public') == True:
						institution_date_obj._public = kwargs['instance']._public
						institution_date_obj._visibility_option = kwargs['instance']._visibility_option
						institution_date_obj._tags = kwargs['instance']._tags

			institution_date_obj.save()


		if getattr(kwargs['instance'],'_date_relation_name') == 'department_date':
			department_date_obj = DateDepartmentRelation(
			date=kwargs['instance'],department=kwargs['instance']._authority_relation_obj
			)

			if hasattr(kwargs['instance'], '_announcement_relation_obj'):
				department_date_obj.announcement = kwargs['instance']._announcement_relation_obj

			department_date_obj.save()


		if getattr(kwargs['instance'],'_date_relation_name') == 'class_date':
			class_date_obj = DateClassRelation(
			date=kwargs['instance'],Class=kwargs['instance']._authority_relation_obj
			)

			if hasattr(kwargs['instance'], '_announcement_relation_obj'):
				class_date_obj.announcement = kwargs['instance']._announcement_relation_obj

			class_date_obj.save()


		if getattr(kwargs['instance'],'_date_relation_name') == 'section_date':
			section_date_obj = DateSectionRelation(
			date=kwargs['instance'],section=kwargs['instance']._authority_relation_obj
			)

			if hasattr(kwargs['instance'], '_announcement_relation_obj'):
				section_date_obj.announcement = kwargs['instance']._announcement_relation_obj

			section_date_obj.save()


		if getattr(kwargs['instance'],'_date_relation_name') == 'subject_teacher_date':
			subject_teacher_date_obj = DateSubjectTeacherRelation(
			date=kwargs['instance'],subject_teacher=kwargs['instance']._authority_relation_obj
			)

			if hasattr(kwargs['instance'], '_announcement_relation_obj'):
				subject_teacher_date_obj.announcement = kwargs['instance']._announcement_relation_obj

			subject_teacher_date_obj.save()


		if getattr(kwargs['instance'],'_date_relation_name') == 'additional_subject_teacher_date':
			additional_subject_teacher_date_obj = DateAdditionalSubjectTeacherRelation(
			date=kwargs['instance'],additional_subject_teacher=kwargs['instance']._authority_relation_obj
			)

			if hasattr(kwargs['instance'], '_announcement_relation_obj'):
				additional_subject_teacher_date_obj.announcement = kwargs['instance']._announcement_relation_obj

			additional_subject_teacher_date_obj.save()


post_save.connect(create_date_relation, sender=Date, weak=False)
#signal ends