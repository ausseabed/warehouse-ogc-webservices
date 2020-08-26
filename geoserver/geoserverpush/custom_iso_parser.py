from gis_metadata.iso_metadata_parser import IsoParser
from gis_metadata.utils import COMPLEX_DEFINITIONS, CONTACTS, format_xpaths, ParserProperty
from gis_metadata.utils import DATES


class CustomIsoParser(IsoParser):

    def _init_data_map(self):
        super(CustomIsoParser, self)._init_data_map()

        date_begin = 'date_begin'
        self._data_map[date_begin] = 'identificationInfo/MD_DataIdentification/extent/EX_Extent/temporalElement/EX_TemporalExtent/extent/TimePeriod/beginPosition'
        self._metadata_props.add(date_begin)

        date_end = 'date_end'
        self._data_map[date_end] = 'identificationInfo/MD_DataIdentification/extent/EX_Extent/temporalElement/EX_TemporalExtent/extent/TimePeriod/endPosition'
        self._metadata_props.add(date_end)
