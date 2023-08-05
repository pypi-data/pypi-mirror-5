
# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

from wger.manager import models as manager_models

from django.contrib import admin

admin.site.register(manager_models.Workout)
admin.site.register(manager_models.Set)
admin.site.register(manager_models.Day)
admin.site.register(manager_models.WorkoutLog)
admin.site.register(manager_models.UserProfile)

admin.site.register(manager_models.Setting)
