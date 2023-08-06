from django.contrib import admin
from pyinstruments.curvefinder.models import CurveDB, SpecAnCurve, NaCurve, \
                                             ScopeCurve, FitCurveDB

admin.site.register(CurveDB)
admin.site.register(SpecAnCurve)
admin.site.register(NaCurve)
admin.site.register(ScopeCurve)
admin.site.register(FitCurveDB)