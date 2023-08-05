# coding=UTF-8
import json, math, os, urllib

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _
from public_project.forms import *
from public_project.models import *
from public_project.search import get_query, search_for_documents


def check_config_prerequisits():
    missing_cps = []
    
    if SiteConfig.objects.count() != 1:
        missing_cps.append(_("Creation of (exactly) one SiteConfig object in the Django admin \
with the general config params and non-dynamical contents."))
    
    if Project.objects.count() != 1:
        missing_cps.append(_("Creation of (exactly) one Project object in the Django admin \
with general information about the project."))
    if ProjectGoalGroup.objects.count() == 0 or ProjectGoal.objects.count() == 0:
        missing_cps.append(_("Creation of at least one ProjectGoalGroup object in the Django admin \
containing at least one ProjectGoal."))
        
    context = {
      'missing_cps': missing_cps,  
    }
    cp_met = len(missing_cps) == 0
    return cp_met, render_to_response('config_prerequisits.html', context)


def get_project():
    return Project.objects.all()[0]


def get_site_config(request):
    site_config = SiteConfig.objects.all()[0]
    
    site_config.pdf_viewer = 'STANDARD'
    site_config.browser = 'Unknown'
    if 'HTTP_USER_AGENT' in request.META:
        if 'Mozilla'.lower() in request.META['HTTP_USER_AGENT'].lower():
            site_config.pdf_viewer = 'STANDARD'
            site_config.browser = 'Mozilla'
        if 'Safari'.lower() in request.META['HTTP_USER_AGENT'].lower():
            site_config.pdf_viewer = 'STANDARD'
            site_config.browser = 'Safari'
        if 'Chrome'.lower() in request.META['HTTP_USER_AGENT'].lower():
            site_config.pdf_viewer = 'STANDARD'
            site_config.browser = 'Chrome'
        if 'Opera'.lower() in request.META['HTTP_USER_AGENT'].lower():
            site_config.pdf_viewer = 'STANDARD'
            site_config.browser = 'Opera'
        if 'MSIE'.lower() in request.META['HTTP_USER_AGENT'].lower():
            if getattr(settings, 'DPP_IE_COMPATIBLE_PDF_VIEWER', False):
                site_config.pdf_viewer = 'LEGACY'
            else:
                site_config.pdf_viewer = False
            site_config.browser = 'MSIE'
    
    if getattr(settings, 'DPP_PUBLIC_API', False):
        site_config.public_api = True
    else:
        site_config.public_api = False
    
    return site_config


def get_research_request(request):
    if 'research_request_id' in request.GET:
        try:
            research_request = ResearchRequest.objects.get(pk=request.GET['research_request_id'])
            return [research_request,]
        except ResearchRequest.DoesNotExist:
            pass
    return None


def get_user_comment(request):
    if 'comment_id' in request.GET:
        try:
            comment = Comment.objects.get(pk=request.GET['comment_id'])
            return [comment,]
        except Comment.DoesNotExist:
            pass
    return None
    

def validate_research_request_form(request):
    
    if request.method == 'POST' and 'research_request_form' in request.POST:
        if not request.user.has_perm('public_project.can_add_research_request'):
            return "FAILED"
        rr = ResearchRequest()
        rr.nr = request.POST['nr']
        rr.title = request.POST['title']
        rr.description = request.POST['description']
        rr.save()
            
        co1_content_type = ContentType.objects.get(app_label="public_project", model=request.POST['co1_content_type'])
        co1 = co1_content_type.get_object_for_this_type(id=request.POST['co1_id'])
        rr_rel = ResearchRequestRelation()
        rr_rel.research_request = rr
        rr_rel.content_object = co1
        if(request.POST['co1_content_type'] == 'document'):
            rr_rel.page = request.POST['co1_page']
        rr_rel.save()
            
        counter_more_cos = int(request.POST['counter_more_cos'])
            
        for num_id in range(2, counter_more_cos + 2):
            if 'co' + str(num_id) + '_id' in request.POST:
                co_content_type = ContentType.objects.get(app_label="public_project", model=request.POST['co' + str(num_id) + '_content_type'])
                co = co_content_type.get_object_for_this_type(id=request.POST['co' + str(num_id) + '_id'])
                rr_rel = ResearchRequestRelation()
                rr_rel.research_request = rr
                rr_rel.content_object = co
                if(request.POST['co' + str(num_id) + '_content_type'] == 'document'):
                    rr_rel.page = request.POST['co' + str(num_id) + '_page']
                rr_rel.save()        
        return "SENT"
    
    return ""


def validate_comment_form(request):
    
    if request.method == 'POST' and 'comment_form' in request.POST:
        print request.POST
        form = CommentForm(request.POST)
        if form.is_valid():
            c = Comment()
            c.username = form.cleaned_data['username']
            c.email = form.cleaned_data['email']
            c.comment = form.cleaned_data['comment']
            c.feedback_allowed = form.cleaned_data['feedback_allowed']
            c.activation_hash = os.urandom(16).encode('hex')
            c.save()
            
            co1_content_type = ContentType.objects.get(app_label="public_project", model=form.cleaned_data['co1_content_type'])
            co1 = co1_content_type.get_object_for_this_type(id=form.cleaned_data['co1_id'])
            cr = CommentRelation()
            cr.comment = c
            cr.content_object = co1
            if(form.cleaned_data['co1_content_type'] == 'document'):
                cr.page = form.cleaned_data['co1_page']
            cr.save()
            
            counter_more_cos = int(request.POST['counter_more_cos'])
            
            for num_id in range(2, counter_more_cos + 2):
                if 'co' + str(num_id) + '_id' in request.POST:
                    co_content_type = ContentType.objects.get(app_label="public_project", model=request.POST['co' + str(num_id) + '_content_type'])
                    co = co_content_type.get_object_for_this_type(id=request.POST['co' + str(num_id) + '_id'])
                    cr = CommentRelation()
                    cr.comment = c
                    cr.content_object = co
                    if(request.POST['co' + str(num_id) + '_content_type'] == 'document'):
                        cr.page = request.POST['co' + str(num_id) + '_page']
                    cr.save()
            
            email_users = User.objects.filter(userprofile__receive_new_comment_emails=True)
            
            #try:
            for i in range(0,1):
                for user in email_users:
                    sep = "-----------------------------------------------------------\n"
                    subject = _("NEW_COMMENT_EMAIL_SUBJECT") + ': ' + unicode(c)
                    
                    msg  = _("NEW_COMMENT_EMAIL_MESSAGE") + "\n"
                    msg += 'http://%s%s' % (Site.objects.get_current().domain, c.get_absolute_url()) + "\n\n"
                    msg += sep
                    msg += _("Name") + ": " + unicode(c.username) + "\n"
                    msg += _("E-Mail") + ": " + unicode(c.email) + "\n"
                    if c.feedback_allowed:
                        fa_str = _("yes")
                    else:
                        fa_str = _("no")
                    msg += _("Questions via mail allowed") + ": " + fa_str + "\n"
                    msg += _("Comment") + ":\n"
                    msg += c.comment + "\n" + sep
                    
                    msg += _("Comment on") + ":" + "\n"
                    for cr in c.commentrelation_set.all():
                        msg += unicode(cr.content_object) + "\n"
                        msg += 'http://%s%s' % (Site.objects.get_current().domain, cr.content_object.get_absolute_url()) + "\n"
                    
                    msg += "\n"
                    
                    if user.has_perm('public_project.change_comment') and user.email:
                        msg += _("NEW_COMMENT_EMAIL_MESSAGE_ACTIVATION") + "\n"
                        msg += 'http://%s/%s?activation_hash=%s&user=%s' \
                            % (Site.objects.get_current().domain, _("activate_comment_url"), c.activation_hash, urllib.quote_plus(unicode(user))) + "\n"
                    
                    send_mail(subject, msg, settings.EMAIL_FROM, [user.email], fail_silently=False)
            #except AttributeError:
            #    pass
            
            return "SENT"
        else:
            print form.errors
            return "FAILED"
    return ""


def merge_with_search_tag_docs(document_list, object):
    for tag in object.search_tags.all():
        search_docs = search_for_documents(tag.name)
        for doc in search_docs:
            if doc in document_list:
                index = document_list.index(doc)
                if not hasattr(document_list[index], 'search_tags'):
                    document_list[index].search_tags = []
                document_list[index].search_tags.append(tag.name)
            else:
                document_list.append(doc)
    document_list.sort(key=lambda x:x.title)
    return document_list


def index(request):
    cp, response = check_config_prerequisits()
    if not cp:
        return response
    
    research_request_list = ResearchRequest.objects.all()
    comment_list = Comment.objects.filter(published=True)
    
    if Event.objects.count() > 0:
        latest_event = Event.objects.all()[0]
    else:
        latest_event = None
    if Document.objects.count() > 0:
        latest_document = Document.objects.all()[0]
    else:
        latest_document = None 
    
    context = RequestContext(request, {
        'site_config': get_site_config(request),
        'project': get_project(),
        'category': 'home',
        'current_project_goal_group': ProjectGoalGroup.objects.get_current(),
        'project_part_list': ProjectPart.objects.all(),
        'latest_event': latest_event,
        'latest_document': latest_document,
        'activity_list': ActivityLog.objects.all()[0:5],
        'research_request_list': research_request_list[0:1],
        'num_total_research_requests': len(research_request_list),
        'comment_list': comment_list[0:1],
        'num_total_comments': len(comment_list),
    })
    return render_to_response('index.html', context)


def project(request):
    cp, response = check_config_prerequisits()
    if not cp:
        return response
    
    project_part_list = ProjectPart.objects.all()
    context = RequestContext(request, {
        'site_config': get_site_config(request),
        'project': get_project(),
        'category': 'project',
        'project_goal_group_list': ProjectGoalGroup.objects.all().order_by('event'),
        'project_part_list': project_part_list,
    })
    return render_to_response('project.html', context)


def project_part(request, project_part_id):
    cp, response = check_config_prerequisits()
    if not cp:
        return response
    
    project_part = get_object_or_404(ProjectPart, pk=project_part_id)
    
    document_list = list(project_part.related_documents.order_by("title"))
    document_list = merge_with_search_tag_docs(document_list, project_part)
    
    comment_form_status = validate_comment_form(request)
    
    content_type = ContentType.objects.get(app_label="public_project", model="projectpart")
    comment_list = Comment.objects.filter(commentrelation__content_type=content_type).filter(commentrelation__object_id=project_part.id).filter(published=True).distinct()
    
    context = RequestContext(request, {
        'site_config': get_site_config(request),
        'project': get_project(),
        'user_comment': get_user_comment(request),
        'category': 'project',
        'project_part': project_part,
        'document_list': document_list,
        'comment_form_status': comment_form_status,
        'comment_list': comment_list[0:3],
        'num_total_comments': len(comment_list),
    })
    return render_to_response('project_part.html', context)


def process(request):
    cp, response = check_config_prerequisits()
    if not cp:
        return response
    
    context = RequestContext(request, {
        'site_config': get_site_config(request),
        'project': get_project(),
        'category': 'process',
        'project_goal_group_list': ProjectGoalGroup.objects.all().order_by('event'),
        'chronology_list': Event.objects.all(),
        'latest_event_list': Event.objects.all()[0:5],
    })
    return render_to_response('process.html', context)


def event(request, event_id):
    cp, response = check_config_prerequisits()
    if not cp:
        return response
    
    event = get_object_or_404(Event, pk=event_id)
    
    document_list = list(event.related_documents.order_by("title"))
    document_list = merge_with_search_tag_docs(document_list, event)
    
    comment_form_status = validate_comment_form(request)
    content_type = ContentType.objects.get(app_label="public_project", model="event")
    comment_list = Comment.objects.filter(commentrelation__content_type=content_type).filter(commentrelation__object_id=event.id).filter(published=True).distinct()
    
    context = RequestContext(request, {
        'site_config': get_site_config(request),
        'project': get_project(),
        'user_comment': get_user_comment(request),
        'category': 'process',
        'event': event,
        'document_list': document_list,
        'comment_form_status': comment_form_status,
        'comment_list': comment_list[0:3],
        'num_total_comments': len(comment_list),
    })
    return render_to_response('event.html', context)


def questions(request):
    cp, response = check_config_prerequisits()
    if not cp:
        return response
    
    project_parts = ProjectPart.objects.all()
    middle = int(math.ceil(float(len(project_parts))/float(2)))
    
    research_request_list = ResearchRequest.objects.all()
    
    context = RequestContext(request, {
        'site_config': get_site_config(request),
        'project': get_project(),
        'category': 'questions',
        'project_part_list_left': project_parts[0:middle],
        'project_part_list_right': project_parts[middle:],
        'research_request_list': research_request_list[0:3],
        'num_total_research_requests': len(research_request_list),
    })
    return render_to_response('questions.html', context)


def question(request, question_id):
    cp, response = check_config_prerequisits()
    if not cp:
        return response
    
    question = get_object_or_404(Question, pk=question_id)
    
    research_request_form_status = validate_research_request_form(request)
    content_type = ContentType.objects.get(app_label="public_project", model="question")
    research_request_list = ResearchRequest.objects.filter(researchrequestrelation__content_type=content_type).filter(researchrequestrelation__object_id=question.id).distinct()
    
    comment_form_status = validate_comment_form(request)
    content_type = ContentType.objects.get(app_label="public_project", model="question")
    comment_list = Comment.objects.filter(commentrelation__content_type=content_type).filter(commentrelation__object_id=question.id).filter(published=True).distinct()
    
    context = RequestContext(request, {
        'site_config': get_site_config(request),
        'project': get_project(),
        'user_comment': get_user_comment(request),
        'research_request': get_research_request(request),
        'category': 'question',
        'question': question,
        'research_request_form_status': research_request_form_status,
        'research_request_list': research_request_list[0:3],
        'num_total_research_requests': len(research_request_list),
        'comment_form_status': comment_form_status,
        'comment_list': comment_list[0:3],
        'num_total_comments': len(comment_list),
    })
    return render_to_response('question.html', context)


def participants(request):
    cp, response = check_config_prerequisits()
    if not cp:
        return response
    
    context = RequestContext(request, {
        'site_config': get_site_config(request),
        'project': get_project(),
        'category': 'participants',
        'ad_participant_list': Participant.objects.filter(participant_type='AD'),
        'po_participant_list': Participant.objects.filter(participant_type='PO'),
        'ci_participant_list': Participant.objects.filter(participant_type='CI'),
        'co_participant_list': Participant.objects.filter(participant_type='CO'),
        'se_participant_list': Participant.objects.filter(participant_type='SE'),
        'latest_participant_list': Participant.objects.all().order_by('-date_added')[0:3],
    })
    return render_to_response('participants.html', context)


def participant(request, participant_id):
    cp, response = check_config_prerequisits()
    if not cp:
        return response
    
    participant = get_object_or_404(Participant, pk=participant_id)
    
    document_list = list(participant.related_documents.order_by("title"))
    document_list = merge_with_search_tag_docs(document_list, participant)
    
    comment_form_status = validate_comment_form(request)
    content_type = ContentType.objects.get(app_label="public_project", model="participant")
    comment_list = Comment.objects.filter(commentrelation__content_type=content_type).filter(commentrelation__object_id=participant.id).filter(published=True).distinct()
    
    context = RequestContext(request, {
        'site_config': get_site_config(request),
        'project': get_project(),
        'user_comment': get_user_comment(request),
        'category': 'participants',
        'participant': participant,
        'document_list': document_list,
        'comment_form_status': comment_form_status,
        'comment_list': comment_list[0:3],
        'num_total_comments': len(comment_list),
    })
    return render_to_response('participant.html', context)


def documents(request):
    cp, response = check_config_prerequisits()
    if not cp:
        return response
    
    project_parts = ProjectPart.objects.all()
    middle = int(math.ceil(float(len(project_parts))/float(2)))
    
    context = RequestContext(request, {
        'site_config': get_site_config(request),
        'project': get_project(),
        'category': 'documents',
        'project_part_list_left': project_parts[0:middle],
        'project_part_list_right': project_parts[middle:],
        'latest_document_list': Document.objects.all()[0:3],
    })
    return render_to_response('documents.html', context)


def xhr_universal_search(request):
    if request.method == 'GET' and 'query' in request.GET:
        query_string = request.GET['query']
        
        entry_query = get_query(query_string, ['name',])
        pp_list = list(ProjectPart.objects.select_related().filter(entry_query)[0:10])
        
        entry_query = get_query(query_string, ['title',])
        q_list = list(Question.objects.select_related().filter(entry_query)[0:10])
        
        entry_query = get_query(query_string, ['name',])
        p_list = list(Participant.objects.select_related().filter(entry_query)[0:10])
        
        entry_query = get_query(query_string, ['title',])
        e_list = list(Event.objects.select_related().filter(entry_query)[0:10])
        
        entry_query = get_query(query_string, ['title',])
        d_list = list(Document.objects.select_related().filter(entry_query)[0:10])
        
        object_list = pp_list + q_list + p_list + e_list + d_list
        
        res = {
            'values': {},
            'options': [],
        }
        
        for object in object_list:
            content_type = object.__class__.__name__.lower()
            id = object.id
            
            if not (content_type == request.GET['ommit_content_type'] and str(id) == request.GET['ommit_id']):
                option = '<i class="' + object.get_icon_class() + '"></i> ' + unicode(object)
                res['values'][option] = {
                    'content_type': content_type,
                    'id': id,
                }
                res['options'].append(option)
        
        mimetype = 'application/javascript'
        return HttpResponse(json.dumps(res), mimetype)


def xhr_document_tags(request):
    if request.method == 'POST':
        
        colors = {
            'projectpart': '#0d9434',
            'participant': '#3e3ec7',
            'event': '#c91a1a',
        }
        if request.POST['document_id']:
            document = get_object_or_404(Document, pk=request.POST['document_id'])
            if request.POST['content_type']:
                cache_entries = SearchTagCacheEntry.objects.filter(document=document).filter(tag__content_type__model=request.POST['content_type'])
            else:
                cache_entries = SearchTagCacheEntry.objects.filter(document=document)
            cache_entries = cache_entries[0:16]
            size_start = 14
            size_span = 10
        else:
            cache_entries = []
            if request.POST['content_type']:
                search_tags = SearchTag.objects.filter(content_type__model=request.POST['content_type']).annotate(num_cache_entries=Count('searchtagcacheentry')).order_by('-num_cache_entries')[0:22]
            else:
                search_tags = SearchTag.objects.annotate(num_cache_entries=Count('searchtagcacheentry')).order_by('-num_cache_entries')[0:22]
            for st in search_tags:
                if(st.searchtagcacheentry_set.count() > 0):
                    ce = st.searchtagcacheentry_set.all()[0]
                    ce.num_results = st.searchtagcacheentry_set.count()
                    cache_entries.append(ce)
            size_start = 16
            size_span = 12
        
        if len(cache_entries) > 0:
            first = cache_entries[0]
            max_num_results = first.num_results
        
        words = []
        for ce in cache_entries:
            text = ce.tag.name
            size = size_start + int(round((float(ce.num_results)/ float(max_num_results)) * size_span))
            color = colors[ce.tag.content_type.model]
            
            word = { "text": text, "size":size, "color": color, }
            words.append(word)
        
        data = json.dumps(words)
        
        mimetype = 'application/javascript'
        return HttpResponse(data, mimetype)


def document(request, document_id):
    
    cp, response = check_config_prerequisits()
    if not cp:
        return response
    
    document = get_object_or_404(Document, pk=document_id)
    comment_form_status = validate_comment_form(request)
    
    query_string = ''
    found_pages = []
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        entry_query = get_query(query_string, ['document__title', 'content',])
        found_pages = Page.objects.select_related().filter(document=document).filter(entry_query).order_by('number')
    
    content_type = ContentType.objects.get(app_label="public_project", model="document")
    tmp_comment_list = Comment.objects.filter(commentrelation__content_type=content_type).filter(commentrelation__object_id=document.id).filter(published=True).distinct()
    print len(tmp_comment_list)
    comment_list = []
    for comment in tmp_comment_list:
        print type(comment)
        cr = comment.commentrelation_set.filter(document=document)[0]
        comment.page = cr.page
        comment_list.append(comment)
    comment_list.sort(key=lambda x:x.page)
    
    context = RequestContext(request, {
        'site_config': get_site_config(request),
        'project': get_project(),
        'user_comment': get_user_comment(request),
        'category': 'documents',
        'document': document,
        'found_pages': found_pages,
        'comment_form_status': comment_form_status,
        'comment_list': comment_list,
        'num_total_comments': len(comment_list),
        'query_string': query_string,
    })
    return render_to_response('document.html', context)


def search(request):
    
    if ('q' in request.GET) and request.GET['q'].strip():
        
        query_string = request.GET['q']
        
        entry_query = get_query(query_string, ['name', 'description',])
        project_part_list = ProjectPart.objects.select_related().filter(entry_query)
        
        entry_query = get_query(query_string, ['title', 'description',])
        question_list = Question.objects.select_related().filter(entry_query)
        
        entry_query = get_query(query_string, ['name', 'description',])
        participant_list = Participant.objects.select_related().filter(entry_query)
        
        entry_query = get_query(query_string, ['title', 'description',])
        event_list = Event.objects.select_related().filter(entry_query)
        
        document_list = search_for_documents(query_string)
        
        context = RequestContext(request, {
            'site_config': get_site_config(request),
            'project': get_project(),
            'category': 'search',
            'query': query_string,
            'project_part_list': project_part_list,
            'question_list': question_list,
            'participant_list': participant_list,
            'event_list': event_list,
            'document_list': document_list,
            'q': query_string,
        })
        
        return render_to_response('search.html', context)
    else:
        return HttpResponse("An Error occured!")


def research_requests(request, object_id, content_type):
    
    if not content_type:
        object = None
        research_request_list = ResearchRequest.objects.all()
    
    if content_type == 'question':
        object = get_object_or_404(Question, pk=object_id)
        content_type = ContentType.objects.get(app_label="public_project", model="question")
        research_request_list = ResearchRequest.objects.filter(researchrequestrelation__content_type=content_type).filter(researchrequestrelation__object_id=object.id).distinct()
    
    ph_title = unicode(object)
    
    context = RequestContext(request, {
        'site_config': get_site_config(request),
        'project': get_project(),
        'rr_object': object,
        'research_request_list': research_request_list,
        'num_total_research_requests': len(research_request_list),
        'content_type': content_type,
        'ph_title': ph_title,    
    })    
    
    return render_to_response('research_requests.html', context)


def comments(request, object_id, content_type):
    
    if not content_type:
        object = None
        comment_list = Comment.objects.filter(published=True)
    
    if content_type == 'project_part':
        object = get_object_or_404(ProjectPart, pk=object_id)
        content_type = ContentType.objects.get(app_label="public_project", model="projectpart")
        comment_list = Comment.objects.filter(commentrelation__content_type=content_type).filter(commentrelation__object_id=object.id).filter(published=True).distinct()
    if content_type == 'question':
        object = get_object_or_404(Question, pk=object_id)
        content_type = ContentType.objects.get(app_label="public_project", model="question")
        comment_list = Comment.objects.filter(commentrelation__content_type=content_type).filter(commentrelation__object_id=object.id).filter(published=True).distinct()
    if content_type == 'participant':
        object = get_object_or_404(Participant, pk=object_id)
        content_type = ContentType.objects.get(app_label="public_project", model="participant")
        comment_list = Comment.objects.filter(commentrelation__content_type=content_type).filter(commentrelation__object_id=object.id).filter(published=True).distinct()
    if content_type == 'event':
        object = get_object_or_404(Event, pk=object_id)
        content_type = ContentType.objects.get(app_label="public_project", model="event")
        comment_list = Comment.objects.filter(commentrelation__content_type=content_type).filter(commentrelation__object_id=object.id).filter(published=True).distinct()
    if content_type == 'document':
        object = get_object_or_404(Document, pk=object_id)
        content_type = ContentType.objects.get(app_label="public_project", model="document")
        comment_list = Comment.objects.filter(commentrelation__content_type=content_type).filter(commentrelation__object_id=object.id).filter(published=True).distinct()
    
    ph_title = unicode(object)
    
    context = RequestContext(request, {
        'site_config': get_site_config(request),
        'project': get_project(),
        'commented_object': object,
        'comment_list': comment_list,
        'num_total_comments': len(comment_list),
        'content_type': content_type,
        'ph_title': ph_title,    
    })    
    
    return render_to_response('comments.html', context)


def api(request):
    cp, response = check_config_prerequisits()
    if not cp:
        return response
    
    context = RequestContext(request, {
        'site_config': get_site_config(request),
        'project': get_project(),
    })
    return render_to_response('api.html', context)


def contact(request):
    cp, response = check_config_prerequisits()
    if not cp:
        return response
    
    image_list = Image.objects.all()
    
    context = RequestContext(request, {
        'site_config': get_site_config(request),
        'project': get_project(),
        'image_list': image_list,
    })
    return render_to_response('contact.html', context)


def activate_comment(request):
    c = get_object_or_404(Comment, activation_hash=request.GET['activation_hash'])
    site_config = get_site_config(request)
    
    res  = '<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>'
    res += '<div style="margin:20px;padding:20px;border:1px solid #999;float:left;color:#333;font-size:14px;'
    res += 'font-family:arial, helvetica, sans-serif;">'
    
    if not c.published:
        c.published = True
        c.published_by = request.GET['user']
        c.save()
        res += _("The following comment was activated for publication on website:") + '<br><br>'
        res += unicode(c)
        
        #User mail
        subject = _("Your comment on %s was published") % site_config.short_title
                    
        msg  = _("Hello %s,") % c.username + "\n\n"
        msg += _("thank you for your comment, which you can find under the following url:") + "\n"
        msg += 'http://%s%s' % (Site.objects.get_current().domain, c.get_absolute_url()) + "\n\n"
        
        msg += _("You can use the url above to tell others about your comment.") + "\n\n"
        
        msg += _("If you want to share your comment on a social network,") + "\n"
        msg += _("you can use the following share urls as a staring point:") + "\n\n"
        
        msg += "Twitter:\n" + c.get_twitter_url() + "\n\n"
        msg += "Facebook:\n" + c.get_facebook_url() + "\n\n"
        msg += "Google+:\n" + c.get_google_plus_url() + "\n\n"
        msg += "App.net:\n" + c.get_app_net_url() + "\n\n\n"
        
        msg += _("Greetings") + "\n\n"
        msg += _("Your %s team") % site_config.short_title + "\n"

        send_mail(subject, msg, settings.EMAIL_FROM, [c.email,], fail_silently=False)
        
        al = ActivityLog()
        al.content_object = c
        al.type = 'NC'
        al.save()
        
    else:
        res += _("Comment already activated by user %s.") % (c.published_by)
    
    res += '</div></body></html>'
    
    return HttpResponse(res)


def custom_404_view(request):
    cp, response = check_config_prerequisits()
    if not cp:
        return response
    
    context = RequestContext(request, {
        'site_config': get_site_config(request),
        'project': get_project(),
    })
    return render_to_response('404.html', context)
    
    