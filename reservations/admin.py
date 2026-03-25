from django.contrib import admin
from .models import ReservationBatch, Reservation


class ReservationInline(admin.TabularInline):
    model = Reservation
    extra = 0
    can_delete = False
    fields = ('book', 'status', 'created_at', 'updated_at')
    readonly_fields = ('book', 'created_at', 'updated_at')
    show_change_link = True
    
    def has_add_permission(self, request, obj=None):
        # ห้ามเพิ่มหนังสือใหม่ใน reservation batch
        return False


@admin.register(ReservationBatch)
class ReservationBatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'expires_at', 'reservation_count', 'created_at', 'updated_at')
    list_filter = ('status', 'expires_at', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 20
    inlines = [ReservationInline]
    readonly_fields = ('user', 'expires_at', 'created_at', 'updated_at', 'reservation_count')
    
    fieldsets = (
        ('Reservation Information', {
            'fields': ('user', 'expires_at', 'reservation_count')
        }),
        ('Admin Actions', {
            'fields': ('status',),
            'description': 'อนุมัติหรือยกเลิกการจองหนังสือ'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # ห้าม admin สร้าง reservation batch ใหม่
        return False
    
    def has_delete_permission(self, request, obj=None):
        # ห้ามลบ reservation batch (ใช้ status cancelled แทน)
        return False
    
    def reservation_count(self, obj):
        return obj.reservations.count()
    reservation_count.short_description = 'Books Reserved'


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'reservation_batch_id', 'batch_user', 'batch_status', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'reservation_batch__status')
    search_fields = ('book__title', 'reservation_batch__user__username', 'reservation_batch__user__email')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_select_related = ('book', 'reservation_batch', 'reservation_batch__user')
    list_per_page = 20
    readonly_fields = ('reservation_batch', 'book', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Reservation Details', {
            'fields': ('reservation_batch', 'book')
        }),
        ('Admin Actions', {
            'fields': ('status',),
            'description': 'อนุมัติหรือยกเลิกการจองหนังสือแต่ละเล่ม'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # ห้าม admin สร้าง reservation ใหม่
        return False
    
    def has_delete_permission(self, request, obj=None):
        # ห้ามลบ reservation (ใช้ status cancelled แทน)
        return False
    
    def batch_user(self, obj):
        return obj.reservation_batch.user.username
    batch_user.short_description = 'User'
    batch_user.admin_order_field = 'reservation_batch__user__username'
    
    def batch_status(self, obj):
        return obj.reservation_batch.status
    batch_status.short_description = 'Batch Status'
    batch_status.admin_order_field = 'reservation_batch__status'
    
    def reservation_batch_id(self, obj):
        return f"#{obj.reservation_batch.id}"
    reservation_batch_id.short_description = 'Batch'
    reservation_batch_id.admin_order_field = 'reservation_batch__id'
