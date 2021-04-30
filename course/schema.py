import json
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id
from graphql import GraphQLError
from django.db import IntegrityError
from .models import Course, CourseSubjectRelation, Subject, SubjectTopicRelation, Topic, TopicSubTopicRelation, SubTopic




class CourseNode(DjangoObjectType):
    class Meta:
        model = Course
        filter_fields = []
        interfaces = (relay.Node, )


class CourseSubjectRelationNode(DjangoObjectType):
    class Meta:
        model = CourseSubjectRelation
        filter_fields = []
        interfaces = (relay.Node, )

class SubjectNode(DjangoObjectType):
    class Meta:
        model = Subject
        filter_fields = []
        interfaces = (relay.Node, )


class SubjectTopicRelationNode(DjangoObjectType):
    class Meta:
        model = SubjectTopicRelation
        filter_fields = []
        interfaces = (relay.Node, )


class TopicNode(DjangoObjectType):
    class Meta:
        model = Topic
        filter_fields = []
        interfaces = (relay.Node, )


class TopicSubTopicRelationNode(DjangoObjectType):
    class Meta:
        model = TopicSubTopicRelation
        filter_fields = []
        interfaces = (relay.Node, )


class SubTopicNode(DjangoObjectType):
    class Meta:
        model = SubTopic
        filter_fields = []
        interfaces = (relay.Node, )




class Query(graphene.ObjectType):
    course = relay.Node.Field(CourseNode)
    all_course = DjangoFilterConnectionField(CourseNode)

    course_subject = relay.Node.Field(CourseSubjectRelationNode)
    all_course_subject = DjangoFilterConnectionField(CourseSubjectRelationNode)

    subject = relay.Node.Field(SubjectNode)
    all_subject = DjangoFilterConnectionField(SubjectNode)

    subject_topic = relay.Node.Field(SubjectTopicRelationNode)
    all_subject_topic = DjangoFilterConnectionField(SubjectTopicRelationNode)

    topic = relay.Node.Field(TopicNode)
    all_topic = DjangoFilterConnectionField(TopicNode)

    topic_subTopic = relay.Node.Field(TopicSubTopicRelationNode)
    all_topic_subTopic = DjangoFilterConnectionField(TopicSubTopicRelationNode)

    subTopic = relay.Node.Field(SubTopicNode)
    all_subTopic = DjangoFilterConnectionField(SubTopicNode)









class CourseSubjectCreationMutation(relay.ClientIDMutation):
    course = graphene.Field(CourseNode)
    subject = graphene.Field(SubjectNode)

    class Input:
        course_json = graphene.String(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        json_string = input.get('course_json')
        json_data = json.loads(json_string)

        if "course" in json_data:
            course = json_data["course"]
            course_obj = Course(name=course["course_name"], innecials=course["course_innecials"])
            queryset = Course.objects.filter(name=course["course_name"]).last()
            if queryset:
                version = queryset.version+1
                course_obj.version = version
                course_obj.save()
            else:
                course_obj.version = 1
                course_obj.save()

            if "course_subject" in course:
                for course_subject in course["course_subject"]:
                    subject_obj = Subject.objects.get(id=from_global_id(course_subject)[1])
                    CourseSubjectRelation.objects.create(course=course_obj,subject=subject_obj)

            if "subject_detail" in course:
                for subjects in course["subject_detail"]:
                    subject_obj = Subject(name=subjects["subject_name"])
                    queryset = Subject.objects.filter(name=subjects["subject_name"]).last()
                    if queryset:
                        version = queryset.version+1
                        subject_obj.version = version
                        subject_obj.save()
                    else:
                        subject_obj.version = 1
                        subject_obj.save()

                    CourseSubjectRelation.objects.create(course=course_obj,subject=subject_obj)

                    if "subject_topic" in subjects:
                        for subject_topic in subjects["subject_topic"]:
                            topic_obj = Topic.objects.get(id=from_global_id(subject_topic)[1])
                            SubjectTopicRelation.objects.create(subject=subject_obj,topic=topic_obj)

                    if "topic_detail" in subjects:
                        for topic_detail in subjects["topic_detail"]:
                            topic_obj = Topic(name=topic_detail["topic_name"])
                            queryset = Topic.objects.filter(name=topic_detail["topic_name"]).last()
                            if queryset:
                                version = queryset.version+1
                                topic_obj.version = version
                                topic_obj.save()
                            else:
                                topic_obj.version = 1
                                topic_obj.save()

                            SubjectTopicRelation.objects.create(subject=subject_obj,topic=topic_obj)

                            if "topic_subTopic" in topic_detail:
                                for topic_subTopic in topic_detail["topic_subTopic"]:
                                    subTopic_obj = SubTopic.objects.get(id=from_global_id(topic_subTopic)[1])
                                    TopicSubTopicRelation.objects.create(sub_topic=subTopic_obj,topic=topic_obj)

                            if "subTopic_detail" in topic_detail:
                                for subTopic_detail in topic_detail["subTopic_detail"]:
                                    try:
                                        subTopic_obj = SubTopic.objects.create(name=subTopic_detail)
                                    except IntegrityError:
                                        subTopic_obj = SubTopic.objects.get(name=subTopic_detail)
                                    TopicSubTopicRelation.objects.create(sub_topic=subTopic_obj,topic=topic_obj)

            return CourseSubjectCreationMutation(course=course_obj) 


        elif "subjects" in json_data:
            subjects = json_data["subjects"]
            subject_obj = Subject(name=subjects["subject_name"])
            queryset = Subject.objects.filter(name=subjects["subject_name"]).last()
            if queryset:
                version = queryset.version+1
                subject_obj.version = version
                subject_obj.save()
            else:
                subject_obj.version = 1
                subject_obj.save()

            if "subject_topic" in subjects:
                for subject_topic in subjects["subject_topic"]:
                    topic_obj = Topic.objects.get(id=from_global_id(subject_topic)[1])
                    SubjectTopicRelation.objects.create(subject=subject_obj,topic=topic_obj)

            if "topic_detail" in subjects:
                for topic_detail in subjects["topic_detail"]:
                    topic_obj = Topic(name=topic_detail["topic_name"])
                    queryset = Topic.objects.filter(name=topic_detail["topic_name"]).last()
                    if queryset:
                        version = queryset.version+1
                        topic_obj.version = version
                        topic_obj.save()
                    else:
                        topic_obj.version = 1
                        topic_obj.save()

                    SubjectTopicRelation.objects.create(subject=subject_obj,topic=topic_obj)

                    if "topic_subTopic" in topic_detail:
                        for topic_subTopic in topic_detail["topic_subTopic"]:
                            subTopic_obj = SubTopic.objects.get(id=from_global_id(topic_subTopic)[1])
                            TopicSubTopicRelation.objects.create(sub_topic=subTopic_obj,topic=topic_obj)

                    if "subTopic_detail" in topic_detail:
                        for subTopic_detail in topic_detail["subTopic_detail"]:
                            try:
                                subTopic_obj = SubTopic.objects.create(name=subTopic_detail)
                            except IntegrityError:
                                subTopic_obj = SubTopic.objects.get(name=subTopic_detail)
                            TopicSubTopicRelation.objects.create(sub_topic=subTopic_obj,topic=topic_obj)

            return CourseSubjectCreationMutation(subject=subject_obj)







class Mutation(graphene.ObjectType):
    course_subject_creation = CourseSubjectCreationMutation.Field()



'''
course
x = {
    "course":{ -optional
        "course_name":"",
        "course_innecials":"",
        "course_subject":[] -optional
        "subject_detail":[
            {
                "subject_name":"",
                "subject_topic":[] -optional
                "topic_detail":[ -optional
                    {
                        "topic_name":"",
                        "topic_subTopic":[] -optional
                        "subTopic_detail":[] -optional
                    }
                ] 
            }   
        ]
    },
    "subjects":{
        "subject_name":"",
        "subject_topic":[] -optional
        "topic_detail":[ -optional
            {
                "topic_name":"",
                "topic_subTopic":[] -optional
                "subTopic_detail":[] -optional
            }
        ] 
    }
}
'''