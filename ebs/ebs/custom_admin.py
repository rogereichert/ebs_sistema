from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from django.template.response import TemplateResponse

class CustomAdminSite(admin.AdminSite):
    site_header = "Sistema EBS"
    site_title = "Sistema EBS"
    index_title = "Painel de Administração"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/sla/', self.admin_view(self.sla_dashboard_view), name='sla-dashboard'),
        ]
        return custom_urls + urls

    def sla_dashboard_view(self, request):
        return TemplateResponse(request, "dashboard/sla_dashboard.html", {})
