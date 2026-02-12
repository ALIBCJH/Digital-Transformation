from django.contrib import admin
from .models import (
    OrganizationUnit, User, Member, Guest, AttendanceLog,
    LeadershipHistory, ServiceSchedule, DataEntryQuota, AltarStatistics
)


@admin.register(OrganizationUnit)
class OrganizationUnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'parent', 'current_leader', 'is_active']
    list_filter = ['level', 'is_active']
    search_fields = ['name']
    raw_id_fields = ['parent', 'current_leader']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone_number', 'home_altar', 'is_active']
    list_filter = ['is_active', 'phone_verified']
    search_fields = ['username', 'email', 'phone_number']
    raw_id_fields = ['home_altar']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone_number', 'gender', 'home_altar', 'is_active']
    list_filter = ['gender', 'is_active']
    search_fields = ['full_name', 'phone_number']
    raw_id_fields = ['home_altar']


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone_number', 'visiting_from', 'visit_count', 'first_visit_date']
    search_fields = ['full_name', 'phone_number']


@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = ['get_person', 'altar', 'service_date', 'service_type', 'recorded_by']
    list_filter = ['service_date', 'service_type', 'country', 'region']
    search_fields = ['member__full_name', 'guest__full_name']
    raw_id_fields = ['member', 'guest', 'altar', 'sub_region', 'region', 'country', 'continent', 'recorded_by']
    date_hierarchy = 'service_date'
    
    def get_person(self, obj):
        return obj.member.full_name if obj.member else obj.guest.full_name
    get_person.short_description = 'Person'


@admin.register(LeadershipHistory)
class LeadershipHistoryAdmin(admin.ModelAdmin):
    list_display = ['leader', 'organization_unit', 'leadership_title', 'start_date', 'end_date']
    list_filter = ['leadership_title', 'end_date']
    search_fields = ['leader__username', 'organization_unit__name']
    raw_id_fields = ['organization_unit', 'leader', 'transferred_to', 'created_by']
    date_hierarchy = 'start_date'


@admin.register(ServiceSchedule)
class ServiceScheduleAdmin(admin.ModelAdmin):
    list_display = ['organization_unit', 'day_of_week', 'service_type', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'service_type', 'is_active']
    search_fields = ['organization_unit__name']
    raw_id_fields = ['organization_unit']


@admin.register(DataEntryQuota)
class DataEntryQuotaAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'attendance_records_created', 'guests_registered']
    list_filter = ['date']
    search_fields = ['user__username']
    raw_id_fields = ['user']
    date_hierarchy = 'date'


@admin.register(AltarStatistics)
class AltarStatisticsAdmin(admin.ModelAdmin):
    list_display = ['altar', 'date', 'total_attendance', 'member_attendance', 'guest_count', 'is_anomaly']
    list_filter = ['date', 'is_anomaly', 'reviewed_by_admin']
    search_fields = ['altar__name']
    raw_id_fields = ['altar']
    date_hierarchy = 'date'
