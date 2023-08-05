# Django settings
TEMPLATE_LOADERS = (
    'wq.db.rest.template.Loader',
    'django.template.loaders.app_directories.Loader',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'wq.db.rest.auth.context_processors.is_authenticated',
    'wq.db.rest.auth.context_processors.social_auth',
    'wq.db.rest.auth.context_processors.csrftoken',
    'wq.db.rest.context_processors.version',
)
SESSION_COOKIE_HTTPONLY = False

# Django Rest Framework settings
REST_FRAMEWORK = {
    'PAGINATE_BY': 50,
    'PAGINATE_BY_PARAM': 'limit',
    'DEFAULT_RENDERER_CLASSES': (
         'rest_framework.renderers.TemplateHTMLRenderer',
         'rest_framework.renderers.JSONRenderer',
         'wq.db.rest.renderers.AMDRenderer',
    ),
    'DEFAULT_MODEL_SERIALIZER_CLASS': 'wq.db.rest.serializers.ModelSerializer',
    'DEFAULT_PAGINATION_SERIALIZER_CLASS': 'wq.db.rest.serializers.PaginationSerializer',
    'DEFAULT_PERMISSION_CLASSES': (
        'wq.db.rest.permissions.ModelPermissions',
    ),
    'FILTER_BACKEND': 'wq.db.rest.filters.FilterBackend'
}

# Django Social Auth settings
SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    #'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details',
    'wq.db.rest.auth.pipeline.assign_default_group',
)

# wq.db settings
ANONYMOUS_PERMISSIONS = {}
SRID = 3857
DEFAULT_AUTH_GROUP = "Users"
FORBIDDEN_APPS = (
    'auth',
    'sessions',
    'admin',
    'contenttypes',
    'reversion',
    'south',
    'social_auth'
)
