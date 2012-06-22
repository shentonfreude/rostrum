from django.contrib import admin
from models import App

class AppAdmin(admin.ModelAdmin):
    list_display = ['acronym', 'project_manager_name'] # can use '__unicode__'
    ordering = ['project_manager_name', 'acronym']     # can NOT use '__unicode__' here

    fieldsets = (
        ('Administrative',      {'fields': (('application_type',                 'application_type_previous'),
                                            ('hitss_supported',                  'hitss_supported_previous'),
                                            ('number_of_users',                  'number_of_users_previous'),
                                            ('project_manager_name',             'project_manager_name_previous'),
                                            ('service_request_classs',           'service_request_classs_previous'),
                                            ('service_request_numbers',          'service_request_numbers_previous'),
                                            ('support_class',                    'support_class_previous'),
                                            ),
#                                 'classes': ('collapse',)
                                 }),
        ('Compliance',          {'fields': (('compliance_508',                   'compliance_508_previous'),
                                            ('data_impact_type',                 'data_impact_type_previous'),
                                            ('fips_information_category',        'fips_information_category_previous'),
                                            ('security_plan_number',             'security_plan_number_previous'),
                                            ),
#                                 'classes': ('collapse',)
                                 }),
        ('Description',         {'fields': (('acronym',                          'acronym_previous'),
                                            ('version_number',                   'version_number_previous'),
                                            ('name',                             'name_previous'),
                                            ('software_class',                   'software_class_previous'),
                                            ('user_groups',                      'user_groups_previous'),
                                            ('description',                      'description_previous'),
                                            ('version_change_description',       'version_change_description_previous'),
                                            ),
#                                 'classes': ('collapse',)
                                 }),
        ('Technical',           {'fields': (('architecture_type',                'architecture_type_previous'),
                                            ('dbms_names_and_version',           'dbms_names_and_version_previous'),
                                            ('interface_acronym',                'interface_acronym_previous'),
                                            ('interface_direction',              'interface_direction_previous'),
                                            ('interface_method',                 'interface_method_previous'),
                                            ('internal_or_external_system',      'internal_or_external_system_previous'),
                                            ('network_services_used',            'network_services_used_previous'),
                                            ('servers_application',              'servers_application_previous'),
                                            ('servers_database',                 'servers_database_previous'),
                                            ('servers_report',                   'servers_report_previous'),
                                            ('servers_location',                 'servers_location_previous'),
                                            ('software_names_and_versions',      'software_names_and_versions_previous'),
                                            ('url_link',                         'url_link_previous'),
                                            ('version_status',                   'version_status_previous'),
                                            ),
#                                 'classes': ('collapse',)
                                 })
        )

admin.site.register(App, AppAdmin)

