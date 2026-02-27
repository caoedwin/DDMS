from django.contrib import admin
from .models import RetainedSample, PersonalRetainedSample, RetainedSampleRecord


@admin.register(RetainedSample)
class RetainedSampleAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'Project', 'Owner', 'SampleName', 'Manufacturer', 'SampleBatch',
                'SampleQuantity', 'Retainer', 'RetainStart', 'RetainPeriod',
                'RetainPosition', 'BorrowedQuantity', 'RemainedQuantity',
                'UnderApprovalQuantity', 'ReturnRequestedAt', 'ReturnRequestedQuantity',
                'ReturnReason', 'ReturnedAt', 'ReturnedQuantity'
            )
        }),
    )
    list_display = (
        'Project', 'Owner', 'SampleName', 'Manufacturer', 'SampleBatch',
        'SampleQuantity', 'Retainer', 'RetainStart', 'RetainPeriod',
        'RetainPosition', 'BorrowedQuantity', 'RemainedQuantity',
        'UnderApprovalQuantity', 'ReturnedQuantity', 'created_at'
    )
    list_filter = (
        'Project', 'Owner', 'SampleName', 'Manufacturer', 'SampleBatch',
        'RetainPosition', 'created_at'
    )
    search_fields = (
        'Project', 'Owner', 'SampleName', 'Manufacturer', 'SampleBatch',
        'Retainer'
    )
    list_per_page = 200
    ordering = ('-created_at',)
    list_display_links = ('Project', 'SampleName')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PersonalRetainedSample)
class PersonalRetainedSampleAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'Sample', 'Borrower', 'Status', 'BorrowQuantity', 'BorrowedReson',
        'RemainedQuantity', 'ReturnRequestedQuantity', 'ReturnReason',
        'ReturnedQuantity', 'ApprovedAt', 'ApprovedBy', 'RejectedAt', 'RejectedBy',
        'created_at'
    )
    list_filter = (
        'Status', 'Borrower', 'created_at', 'ApprovedAt', 'RejectedAt'
    )
    search_fields = (
        'Borrower', 'BorrowedReson', 'ReturnReason',
        'Sample__Project', 'Sample__SampleName'
    )
    list_per_page = 100
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(RetainedSampleRecord)
class RetainedSampleRecordAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'Sample', 'RecordType', 'Borrowed', 'BorrowQuantity',
        'BorrowedReson', 'BorrowedStatus', 'ReturnedStatus', 'created_at'
    )
    list_filter = (
        'RecordType', 'BorrowedStatus', 'ReturnedStatus', 'created_at'
    )
    search_fields = (
        'Borrowed', 'BorrowedReson', 'Sample__Project', 'Sample__SampleName'
    )
    list_per_page = 200
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')