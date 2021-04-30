from datetime import timedelta, date
from django.db import models
from django.db.models.signals import post_save
from post.models import Post
from institution.models import Institution
from department.models import Department
from Class.models import Class, ClassSectionRelation, ClassSubjectTeacherRelation, AdditionalSubjectTeacherRelation
from commentExplanation.models import Comment

class Announcement(models.Model):
	STATUS_CHOICE = (
			('draft', 'Draft'),
			('active','Active'),
			('archive','Archived'),
		)

	post = models.OneToOneField(Post, on_delete=models.CASCADE)
	status = models.CharField(max_length=20,choices=STATUS_CHOICE, default='draft')
	block_comment = models.BooleanField(default=False)
	archive_date = models.DateField(auto_now=False, auto_now_add=False,null=True, blank=True)
	publish = models.DateTimeField(auto_now=False, auto_now_add=False ,null=True, blank=True)

	def __str__(self):
		return self.post.title +" / "+ self.status



# announcement creation signal
def create_announcement(sender, **kwargs):
	if kwargs['created']:
		if getattr(kwargs['instance'], '_post_for') == 'announcement':
			announcement_obj = Announcement(post=kwargs['instance'])

			if hasattr(kwargs['instance'], '_status'):
				if getattr(kwargs['instance'], '_status') == 'active':
					announcement_obj.status = kwargs['instance']._status
					announcement_obj.publish = date.today()

					if hasattr(kwargs['instance'], '_block_comment'):
						announcement_obj.block_comment = kwargs['instance']._block_comment

					if hasattr(kwargs['instance'], '_archive_date'):
						announcement_obj.archive_date = kwargs['instance']._archive_date
					else:
						announcement_obj.archive_date = announcement_obj.publish + timedelta(days=10)

			announcement_obj._authority = kwargs['instance']._authority
			announcement_obj._authority_model_obj = kwargs['instance']._authority_model_obj
			announcement_obj.save()

post_save.connect(create_announcement, sender=Post, weak=False)
#signal ends





class CommentAnnouncementRelation(models.Model):
	comment = models.OneToOneField(Comment, on_delete=models.CASCADE)
	announcement = models.ForeignKey('Announcement', on_delete=models.CASCADE)

	def __str__(self):
		return self.comment.body +" / "+ self.announcement.post.title


def create_comment_announcement(sender, **kwargs):
	if kwargs['created']:
		if getattr(kwargs['instance'], '_post_for') == 'announcement':
			CommentAnnouncementRelation.objects.create(
				comment=kwargs['instance'],announcement=kwargs['instance']._post_model_obj
				)



post_save.connect(create_comment_announcement, sender=Comment, weak=False)




class InstitutionAnnouncementRelation(models.Model):
	institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
	announcement = models.OneToOneField('Announcement', on_delete=models.CASCADE)

	def __str__(self):
		return self.institution.name +" / "+ self.announcement.post.title


class DepartmentAnnouncementRelation(models.Model):
	department = models.ForeignKey(Department, on_delete=models.CASCADE)
	announcement = models.OneToOneField('Announcement', on_delete=models.CASCADE)

	def __str__(self):
		return self.department.name +" / "+ self.announcement.post.title


class ClassAnnouncementRelation(models.Model):
	Class = models.ForeignKey(Class, on_delete=models.CASCADE)
	announcement = models.OneToOneField('Announcement', on_delete=models.CASCADE)

	def __str__(self):
		return self.Class.course.name +" / "+ self.announcement.post.title


class SectionAnnouncementRelation(models.Model):
	section = models.ForeignKey(ClassSectionRelation, on_delete=models.CASCADE)
	announcement = models.OneToOneField('Announcement', on_delete=models.CASCADE)

	def __str__(self):
		return self.section.section +" / "+ self.announcement.post.title


class SubjectTeacherAnnouncementRelation(models.Model):
	section_subject = models.ForeignKey(ClassSubjectTeacherRelation, on_delete=models.CASCADE)
	announcement = models.OneToOneField('Announcement', on_delete=models.CASCADE)

	def __str__(self):
		return self.section_subject.subject.subject.name +" / "+ self.announcement.post.title


class AdditionalSubjectTeacherAnnouncementRelation(models.Model):
	section_additional_subject = models.ForeignKey(AdditionalSubjectTeacherRelation, on_delete=models.CASCADE)
	announcement = models.OneToOneField('Announcement', on_delete=models.CASCADE)

	def __str__(self):
		return self.section_additional_subject.subject.subject.name +" / "+ self.announcement.post.title




# announcement relation creation signal
def create_announcement_relation(sender, **kwargs):
	if kwargs['created']:
		if getattr(kwargs['instance'], '_authority') == 'adminUser':
			InstitutionAnnouncementRelation.objects.create(
				institution=kwargs['instance']._authority_model_obj, announcement=kwargs['instance']
				)

		if getattr(kwargs['instance'], '_authority') == 'hod':
			DepartmentAnnouncementRelation.objects.create(
				department=kwargs['instance']._authority_model_obj, announcement=kwargs['instance']
				)

		if getattr(kwargs['instance'], '_authority') == 'classTeacher':
			ClassAnnouncementRelation.objects.create(
				Class=kwargs['instance']._authority_model_obj, announcement=kwargs['instance']
				)

		if getattr(kwargs['instance'], '_authority') == 'sectionTeacher':
			SectionAnnouncementRelation.objects.create(
				section=kwargs['instance']._authority_model_obj, announcement=kwargs['instance']
				)

		if getattr(kwargs['instance'], '_authority') == 'sectionSubjectTeacher':
			SubjectTeacherAnnouncementRelation.objects.create(
				section_subject=kwargs['instance']._authority_model_obj, announcement=kwargs['instance']
				)

		if getattr(kwargs['instance'], '_authority') == 'sectionAdditionalSubjectTeacher':
			AdditionalSubjectTeacherAnnouncementRelation.objects.create(
				section_additional_subject=kwargs['instance']._authority_model_obj, announcement=kwargs['instance']
				)


post_save.connect(create_announcement_relation, sender=Announcement, weak=False)
#signal ends