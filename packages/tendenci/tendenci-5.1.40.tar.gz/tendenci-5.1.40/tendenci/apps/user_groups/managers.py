import operator
from haystack.query import SearchQuerySet

from django.db.models import Manager
from django.db.models import Q
from django.contrib.auth.models import User

from tendenci.core.perms.managers import TendenciBaseManager


class GroupManager(TendenciBaseManager):
    def first(self, **fiters):
        groups = self.filter(status=True,
                             status_detail='active'
                            ).order_by('id')
        if fiters:
            groups = groups.filter(**fiters)
        [group] = groups[:1] or [None]

        return group


class OldGroupManager(Manager):
    def search(self, query=None, *args, **kwargs):
        """
            Uses haystack to query groups. 
            Returns a SearchQuerySet
        """
        sqs = SearchQuerySet()
        user = kwargs.get('user', None)

        # check to see if there is impersonation
        if hasattr(user,'impersonated_user'):
            if isinstance(user.impersonated_user, User):
                user = user.impersonated_user
                
        is_a_superuser = user.profile.is_superuser
            
        if query:
            sqs = sqs.auto_query(sqs.query.clean(query)) 
            if user:
                if not is_a_superuser:
                    if not user.is_anonymous():
                    # if b/w superuser and anon

                        # (status+status_detail+(anon OR user)) OR (who_can_view__exact)
                        anon_query = Q(**{'allow_anonymous_view':True,})
                        user_query = Q(**{'allow_user_view':True,})
                        sec1_query = Q(**{
                            'show_as_option':1,
                            'status':1,
                            'status_detail':'active',
                        })
                        sec2_query = Q(**{
                            'who_can_view__exact':user.username
                        })
                        query = reduce(operator.or_, [anon_query, user_query])
                        query = reduce(operator.and_, [sec1_query, query])
                        query = reduce(operator.or_, [query, sec2_query])

                        sqs = sqs.filter(query)
                    else: # anonymous
                        query = Q(**{
                            'allow_anonymous_view': True,
                            'show_as_option':1,
                            'status':1,
                            'status_detail':'active',
                        })
                        sqs = sqs.filter(query)
            else: # anonymous
                query = Q(**{
                    'allow_anonymous_view': True,
                    'show_as_option':1,
                    'status':1,
                    'status_detail':'active',
                })
                sqs = sqs.filter(query)
        else:
            if user:
                if is_a_superuser:
                    # this is no-op. the .all().exclude(type='membership').models(Group) wouldn't work
                    #sqs = sqs.all()
                    sqs = sqs.filter(status=True)
                else:
                    if not user.is_anonymous():
                        # (status+status_detail+anon OR who_can_view__exact)
                        anon_query = Q(**{'allow_anonymous_view':True,})
                        user_query = Q(**{'allow_user_view':True,})
                        sec1_query = Q(**{
                            'show_as_option':1,
                            'status':1,
                            'status_detail':'active',
                        })
                        sec2_query = Q(**{
                            'who_can_view__exact': user.username
                        })
                        query = reduce(operator.or_, [anon_query, user_query])
                        query = reduce(operator.and_, [sec1_query, query])
                        query = reduce(operator.or_, [query, sec2_query])
                        sqs = sqs.filter(query)
                    else: # anonymous
                        query = Q(**{
                            'allow_anonymous_view': True,
                            'show_as_option':1,
                            'status':1,
                            'status_detail':'active',
                        })
                        sqs = sqs.filter(query)   
            else: # anonymous
                query = Q(**{
                    'allow_anonymous_view': True,
                    'show_as_option':1,
                    'status':1,
                    'status_detail':'active',
                })
                sqs = sqs.filter(query)
        
        sqs = sqs.order_by('-create_dt')
        
        return sqs.models(self.model)
    
