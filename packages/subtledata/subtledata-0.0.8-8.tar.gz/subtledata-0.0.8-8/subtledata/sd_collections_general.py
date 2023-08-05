__author__ = 'gsibble'

from base_types import SDFirstClassObject, SDInterface

class SDGeneralInterface(SDInterface):

    def __init__(self, parent):
        """

        :param parent:
        """
        super(SDGeneralInterface, self).__init__(parent)

    @property
    def states(self):
        """


        :return:
        """
        states = self._swagger_general_api.getAllStates(self._api_key)
        return states

    @property
    def countries(self):
        """


        :return:
        """
        countries = self._swagger_general_api.getAllStates(self._api_key)

        #TODO:  Sort through and get unique countries
        return countries

    @property
    def languages(self):

        #TODO:  Add languages

        """


        :return:
        """
        return []