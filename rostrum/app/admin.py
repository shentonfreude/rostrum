from django.contrib import admin
from models import App

class AppAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Administrative',      {'fields': ('application_type',
                                            'hitss_supported',
                                            'number_of_users',
                                            'project_manager_name',
                                            'service_request_classs',
                                            'service_request_numbers',
                                            'support_class'),
#                                 'classes': ('collapse',)
                                 }),
        ('Compliance',          {'fields': ('compliance_508',
                                            'data_impact_type',
                                            'fips_information_category',
                                            'security_plan_number',
                                            ),
#                                 'classes': ('collapse',)
                                 }),
        ('Description',         {'fields': ('acronym',
                                            'description',
                                            'name',
                                            'software_class',
                                            'user_groups',
                                            'version_change_description',
                                            'version_number',
                                            ),
#                                 'classes': ('collapse',)
                                 }),
        ('Technical',           {'fields': ('architecture_type',
                                            'dbms_names_and_version',
                                            'interface_acronym',
                                            'interface_direction',
                                            'interface_method',
                                            'internal_or_external_system',
                                            'network_services_used',
                                            'servers_application',
                                            'servers_database',
                                            'servers_report',
                                            'servers_location',
                                            'software_names_and_versions',
                                            'url_link',
                                            'version_status',
                                            ),
#                                 'classes': ('collapse',)
                                 })
        )

admin.site.register(App, AppAdmin)

