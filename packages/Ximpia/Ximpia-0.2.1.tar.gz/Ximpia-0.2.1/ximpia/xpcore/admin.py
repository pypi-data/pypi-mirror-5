# coding: utf-8

from models import CoreParam, Application, Menu, View, Action, Workflow, XpTemplate, Setting, MetaKey, WorkflowView
from models import ApplicationMeta, MenuParam, ViewMeta, ViewParamValue, ViewMenu, ViewTmpl, WFParamValue, Param, ViewTag, ApplicationMedia
from models import ApplicationTag, Service, ServiceMenu, ViewAccessGroup, ActionAccessGroup, ServiceMenuCondition, ViewMenuCondition, Condition
from models import SearchIndex, SearchIndexWord, SearchIndexParam, WorkflowMeta, ServiceMeta

from django.contrib import admin

# INLINES 

class ApplicationMetaInline(admin.StackedInline):
	model = ApplicationMeta

class ServiceMenuConditionInline(admin.StackedInline):
	model = ServiceMenuCondition

class ViewMenuConditionInline(admin.StackedInline):
	model = ViewMenuCondition

class ViewMetaInline(admin.StackedInline):
	model = ViewMeta

class MenuParamInline(admin.StackedInline):
	model = MenuParam

class ViewParamValueInline(admin.StackedInline):
	model = ViewParamValue

class ViewMenuInline(admin.StackedInline):
	model = ViewMenu

class ViewTemplateInline(admin.StackedInline):
	model = ViewTmpl

class ViewTagsInline(admin.StackedInline):
	model = ViewTag

class AppTagsInline(admin.StackedInline):
	model = ApplicationTag

class ServiceMenuInline(admin.StackedInline):
	model = ServiceMenu

class ServiceMetaInline(admin.StackedInline):
	model = ServiceMeta

class WorkflowViewParamValueInline(admin.StackedInline):
	model = WFParamValue

class WorkflowMetaInline(admin.StackedInline):
	model = WorkflowMeta

class ApplicationMediaInline(admin.StackedInline):
	model = ApplicationMedia

class ViewAccessGroupInline(admin.StackedInline):
	model = ViewAccessGroup
	raw_id_fields = ('group',)
	related_lookup_fields = {
	        'fk': ['group'],
	    }

class ActionAccessGroupInline(admin.StackedInline):
	model = ActionAccessGroup
	raw_id_fields = ('group',)
	related_lookup_fields = {
	        'fk': ['group'],
	    }

class IndexWordInline(admin.StackedInline):
	model = SearchIndexWord

class IndexParamInline(admin.StackedInline):
	model = SearchIndexParam

# INLINES

class ConditionAdmin(admin.ModelAdmin):
	list_display = ('id','name','userCreateId', 'userModifyId', 'dateCreate', 'dateModify')
	list_display_links = ('name',)
	def save_model(self, request, obj, form, change):
		obj.userModifyId = request.user.id
		if not obj.id:
			obj.userCreateId = request.user.id
		obj.save()

class CoreParamAdmin(admin.ModelAdmin):
	list_display = ('id','mode','name','paramType','value','userCreateId', 'userModifyId', 'dateCreate', 'dateModify')
	list_filter = ('mode','paramType')
	list_display_links = ('name','mode')
	search_fields = ('name',)
	def save_model(self, request, obj, form, change):
		obj.userModifyId = request.user.id
		if not obj.id:
			obj.userCreateId = request.user.id
		obj.save()

class ParamAdmin(admin.ModelAdmin):
	list_display = ('id','name','title','application','paramType','isView','isWorkflow',\
		'userCreateId', 'userModifyId', 'dateCreate', 'dateModify')
	list_filter = ('application__title','paramType','isView','isWorkflow')
	list_display_links = ('name',)
	search_fields = ('title','name')
	def save_model(self, request, obj, form, change):
		obj.userModifyId = request.user.id
		if not obj.id:
			obj.userCreateId = request.user.id
		obj.save()

class ApplicationAdmin(admin.ModelAdmin):
	list_display = ('id','name','slug','title','developer','developerOrg','isSubscription','isPrivate','isAdmin',\
		'userCreateId', 'userModifyId', 'dateCreate', 'dateModify')
	list_display_links = ('name',)
	list_filter = ('isSubscription','isPrivate','isAdmin','category','tags__name')
	search_fields = ('name', 'slug','title')
	raw_id_fields = ('developer','developerOrg','accessGroup')
	related_lookup_fields = {
	        'fk': ['developer','developerOrg','accessGroup'],
	    }
	inlines = [ ApplicationMetaInline, ApplicationMediaInline, AppTagsInline ]
	def save_model(self, request, obj, form, change):
		obj.userModifyId = request.user.id
		if not obj.id:
			obj.userCreateId = request.user.id
		obj.save()

class ServiceAdmin(admin.ModelAdmin):
	list_display = ('id','name', 'application', 'userCreateId', 'userModifyId', 'dateCreate', 'dateModify')
	list_display_links = ('name',)
	list_filter = ('application__title',)
	search_fields = ('name', 'application__name',)
	raw_id_fields = ('application',)
	related_lookup_fields = {
	        'fk': ['application'],
	    }
	exclude = ('implementation',)
	inlines = [ ServiceMenuInline, ServiceMetaInline ]
	def save_model(self, request, obj, form, change):
		obj.userModifyId = request.user.id
		if not obj.id:
			obj.userCreateId = request.user.id
		obj.save()

class ServiceMenuAdmin(admin.ModelAdmin):
	list_display = ('id','menu','service','zone','userCreateId', 'userModifyId', 'dateCreate', 'dateModify')
	list_display_links = ('menu',)
	list_filter = ('service__name',)
	inlines = [ ServiceMenuConditionInline ]
	def save_model(self, request, obj, form, change):
		obj.userModifyId = request.user.id
		if not obj.id:
			obj.userCreateId = request.user.id
		obj.save()

class MenuAdmin(admin.ModelAdmin):
	list_display = ('id','name','title','description','view','application','action','icon','language',\
		'userCreateId', 'userModifyId', 'dateCreate', 'dateModify')
	list_display_links = ('name',)
	list_filter = ('application__title',)
	search_fields = ('description','name','title')
	raw_id_fields = ('application','view','action')
	related_lookup_fields = {
	        'fk': ['application','view','action'],
	    }
	inlines = [ MenuParamInline ]
	def save_model(self, request, obj, form, change):
		obj.userModifyId = request.user.id
		if not obj.id:
			obj.userCreateId = request.user.id
		obj.save()

class ViewAdmin(admin.ModelAdmin):
	list_display = ('id','name','slug','application', 'service', 'winType','hasAuth',\
				'userCreateId', 'userModifyId', 'dateCreate', 'dateModify',)
	list_display_links = ('name',)
	list_filter = ('winType','hasAuth','service__name','application__title')
	search_fields = ('name','slug',)
	raw_id_fields = ('parent',)
	related_lookup_fields = {
	        'fk': ['parent'],
	    }
	inlines = [ ViewMetaInline, ViewParamValueInline, ViewTemplateInline, ViewMenuInline, ViewTagsInline, ViewAccessGroupInline ]
	exclude = ['implementation']
	def save_model(self, request, obj, form, change):
		obj.userModifyId = request.user.id
		if not obj.id:
			obj.userCreateId = request.user.id
		obj.save()

class ViewMenuAdmin(admin.ModelAdmin):
	list_display = ('id','menu','view','zone','userCreateId', 'userModifyId', 'dateCreate', 'dateModify')
	list_display_links = ('menu',)
	list_filter = ('view__name',)
	inlines = [ ViewMenuConditionInline ]
	def save_model(self, request, obj, form, change):
		obj.userModifyId = request.user.id
		if not obj.id:
			obj.userCreateId = request.user.id
		obj.save()

class ActionAdmin(admin.ModelAdmin):
	list_display = ('id','name','slug','application','service','hasAuth','userCreateId', 'userModifyId', 'dateCreate', 'dateModify')
	list_display_links = ('name',)
	list_filter = ('application',)
	search_fields = ('name', 'slug')
	raw_id_fields = ('application',)
	related_lookup_fields = {
	        'fk': ['application',],
	    }
	inlines = [ ActionAccessGroupInline ]
	exclude = ['implementation']
	def save_model(self, request, obj, form, change):
		obj.userModifyId = request.user.id
		if not obj.id:
			obj.userCreateId = request.user.id
		obj.save()

class WorkflowAdmin(admin.ModelAdmin):
	list_display = ('id','code','application', 'userCreateId', 'userModifyId','dateCreate', 'dateModify')
	list_display_links = ('code',)
	list_filter = ('application__title',)
	raw_id_fields = ('application',)
	related_lookup_fields = {
	        'fk': ['application',],
	    }
	inlines = [WorkflowMetaInline]
	def save_model(self, request, obj, form, change):
		obj.userModifyId = request.user.id
		if not obj.id:
			obj.userCreateId = request.user.id
		obj.save()

class WorkflowViewAdmin(admin.ModelAdmin):
	# Commented because goes into infinite loop, hangs system
	#list_display = ('id','order','flow','viewSource','viewTarget','action','userCreateId', 'userModifyId','dateCreate', 'dateModify')
	#list_display = ('id','flow', 'viewSource', 'action', 'viewTarget', 'userCreateId', 'userModifyId','dateCreate', 'dateModify')
	list_display = ('id', 'userCreateId', 'userModifyId','dateCreate', 'dateModify')
	list_display_links = ('id',)
	list_filter = ('flow__code',)
	raw_id_fields = ('flow','viewSource','viewTarget','action')
	related_lookup_fields = {
	        'fk': ['flow','viewSource','viewTarget','action'],
	    }
	inlines = [ WorkflowViewParamValueInline ]
	def save_model(self, request, obj, form, change):
		obj.userModifyId = request.user.id
		if not obj.id:
			obj.userCreateId = request.user.id
		obj.save()

class XpTemplateAdmin(admin.ModelAdmin):
	list_display = ('id','name','alias','application','language','country','winType','device',\
		'userCreateId', 'userModifyId','dateCreate', 'dateModify')
	list_display_links = ('name',)
	list_filter = ('application__title',)
	search_fields = ('name', 'alias',)
	raw_id_fields = ('application',)
	related_lookup_fields = {
	        'fk': ['application','application'],
	    }
	def save_model(self, request, obj, form, change):
		obj.userModifyId = request.user.id
		if not obj.id:
			obj.userCreateId = request.user.id
		obj.save()

class MetaKeyAdmin(admin.ModelAdmin):
	list_display = ('id','name','keyType','userCreateId', 'userModifyId', 'dateCreate', 'dateModify')
	list_display_links = ('name',)
	list_filter = ('keyType__name',)
	ordering = ['name']
	def save_model(self, request, obj, form, change):
		obj.userModifyId = request.user.id
		if not obj.id:
			obj.userCreateId = request.user.id
		obj.save()

class SettingAdmin(admin.ModelAdmin):
	list_display = ('id','name','application','description','mustAutoload','userCreateId', 'userModifyId', 'dateCreate', 'dateModify')
	list_display_links = ('name',)
	list_filter = ('mustAutoload',)
	raw_id_fields = ('application',)
	related_lookup_fields = {
	        'fk': ['application',],
	    }
	ordering = ['name']
	def save_model(self, request, obj, form, change):
		obj.userModifyId = request.user.id
		if not obj.id:
			obj.userCreateId = request.user.id
		obj.save()

class SearchIndexAdmin(admin.ModelAdmin):
	list_display = ('id','title', 'application','view','action','userCreateId', 'userModifyId', 'dateCreate', 'dateModify')
	list_display_links = ('title',)
	list_filter = ('application__slug',)
	search_fields = ('title',)
	raw_id_fields = ('application','view','action',)
	related_lookup_fields = {
	        'fk': ['application','view','action',],
	    }
	inlines = [ IndexWordInline, IndexParamInline ]
	def save_model(self, request, obj, form, change):
		obj.userModifyId = request.user.id
		if not obj.id:
			obj.userCreateId = request.user.id
		obj.save()

admin.site.register(CoreParam, CoreParamAdmin)
admin.site.register(Param, ParamAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(View, ViewAdmin)
admin.site.register(Action, ActionAdmin)
admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(WorkflowView, WorkflowViewAdmin)
admin.site.register(XpTemplate, XpTemplateAdmin)
admin.site.register(MetaKey, MetaKeyAdmin)
admin.site.register(Setting, SettingAdmin)
admin.site.register(SearchIndex, SearchIndexAdmin)
admin.site.register(Condition, ConditionAdmin)
admin.site.register(ServiceMenu, ServiceMenuAdmin)
admin.site.register(ViewMenu, ViewMenuAdmin)
