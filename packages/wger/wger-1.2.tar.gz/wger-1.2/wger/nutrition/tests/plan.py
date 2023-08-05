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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

from wger.nutrition.models import NutritionPlan

from wger.manager.tests.testcase import WorkoutManagerDeleteTestCase
from wger.manager.tests.testcase import WorkoutManagerEditTestCase
from wger.manager.tests.testcase import WorkoutManagerAddTestCase


class DeletePlanTestCase(WorkoutManagerDeleteTestCase):
    '''
    Tests deleting a nutritional plan
    '''

    object_class = NutritionPlan
    url = 'nutrition-delete'
    pk = 2


class EditPlanTestCase(WorkoutManagerEditTestCase):
    '''
    Tests editing an ingredient
    '''

    object_class = NutritionPlan
    url = 'nutrition-edit'
    pk = 2
    data = {'description': 'My new description'}
