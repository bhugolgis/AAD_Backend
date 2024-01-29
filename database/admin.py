from django.contrib import admin
from .models import *

# Register your models here.

class SearchUser(admin.ModelAdmin):
    search_fields = ["name" ,"username" , "phoneNumber"  ]
    list_display = ["phoneNumber" , "name"  ]



admin.site.register(ward)
admin.site.register(healthPost)
admin.site.register(area)
admin.site.register(section)
admin.site.register(CustomUser , SearchUser)
admin.site.register(familyHeadDetails)
admin.site.register(familyMembers)
# admin.site.register(phlebotomist)
# admin.site.register(TestTube)
# admin.site.register(PatientPathlab)
admin.site.register(LabTests)
admin.site.register(PatientPathLabReports)
admin.site.register(refereloptions)
admin.site.register(vulnerableOptions)
admin.site.register(UserApprovalRecords)



