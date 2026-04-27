from django.contrib import admin
from .models import User, Role, UserRole, ApiKey, Session

admin.site.register(User)
admin.site.register(Role)
admin.site.register(UserRole)
admin.site.register(ApiKey)
admin.site.register(Session)
