from typing import Union, List, Optional

from .base_api import BaseApi
from .constants import Constants, Dose, Vaccine
from .utils import today, filter_centers


class CowinAPI(BaseApi):

    def get_states(self):
        url = Constants.states_list_url
        return self._call_api(url)

    def get_districts(self, state_id: str):
        url = f"{Constants.districts_list_url}/{state_id}"
        return self._call_api(url)

    def get_availability_by_base(self, caller: str,
                                 areas: Union[str, List[str]],
                                 date: str, min_age_limit: int,
                                 vaccine: Optional[Vaccine] = None,
                                 dose: Optional[Dose] = None):
        """
        this function is called by the get availability function
        this is separated out so that the parent functions have the same
        structure and development becomes easier
        """
        if caller == 'district':
            area_type, base_url = 'district_id', Constants.availability_by_district_url
        else:
            area_type, base_url = 'pincode', Constants.availability_by_pin_code_url

        # if the areas is a str, convert to list
        if not isinstance(areas, list):
            areas = [areas]

        results = {'centers': []}

        # make a separate call for each of the areas
        for area_id in areas:
            url = f"{base_url}?{area_type}={area_id}&date={date}"
            curr_result = self._call_api(url)
            curr_result = filter_centers(
                centers=curr_result,
                min_age_limit=min_age_limit,
                vaccine=vaccine,
                dose=dose
            )

            # append
            if 'centers' in curr_result:
                results['centers'] += curr_result['centers']

        # return the results in the same format as returned by the api
        return results

    def get_availability_by_district(self, district_id: Union[str, List[str]],
                                     date: str = today(),
                                     min_age_limit: int = None,
                                     vaccine: Optional[Vaccine] = None,
                                     dose: Optional[Dose] = None):
        return self.get_availability_by_base(caller='district', areas=district_id,
                                             date=date, min_age_limit=min_age_limit,
                                             vaccine=vaccine, dose=dose)

    def get_availability_by_pin_code(self, pin_code: Union[str, List[str]],
                                     date: str = today(),
                                     min_age_limit: Optional[int] = None,
                                     vaccine: Optional[Vaccine] = None,
                                     dose: Optional[Dose] = None):
        return self.get_availability_by_base(caller='pin_code', areas=pin_code,
                                             date=date, min_age_limit=min_age_limit,
                                             vaccine=vaccine, dose=dose)
