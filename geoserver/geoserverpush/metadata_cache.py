import logging
import unittest
from unittest.mock import patch, Mock

import requests
from gis_metadata.iso_metadata_parser import IsoParser
from gis_metadata.metadata_parser import get_metadata_parser

from custom_iso_parser import CustomIsoParser


class MetaDataCache():
    def __init__(self):
        self.metadata = {}

    def get_metadata(self, metadata_url):
        if metadata_url in self.metadata:
            return self.metadata[metadata_url]
        else:
            meta = self.download_metadata(metadata_url)
            self.metadata[metadata_url] = meta
            return meta

    def download_metadata(self, metadata_url):
        logging.info("Loading metadata: %s\n" % metadata_url)
        if not(metadata_url.startswith("http://pid") or metadata_url.startswith("https://pid")):
            return None

        try:
            metadata_response = requests.get(
                metadata_url + "?_format=text%2Fxml", timeout=5)
            if (metadata_response.ok):
                iso_from_file = CustomIsoParser(metadata_response.text)
                return iso_from_file
            else:
                logging.warn(
                    "Could not download metadata from: %s\n" % metadata_url)
                logging.warn(
                    "Response {} was returned from attempt to download. Content was {}".format(
                        metadata_response.status_code, metadata_response.text))
                return None

        except Exception:
            logging.warn(
                "Could not load metadata from: %s\n" % metadata_url)
            return None

    def get_abstract(self, metadata_url):
        meta = self.get_metadata(metadata_url)
        abstract = ""
        if (meta != None):
            abstract = meta.abstract
        return abstract + '\n\n' + metadata_url

    def extract_title(self, metadata_url):
        meta = self.get_metadata(metadata_url)
        if (meta == None):
            return ""

        return meta.title

    def extract_start(self, metadata_url):
        meta = self.get_metadata(metadata_url)
        if (meta == None):
            return "N/A"

        return meta.date_begin

    def extract_end(self, metadata_url):
        meta = self.get_metadata(metadata_url)
        if (meta == None):
            return "N/A"

        return meta.date_end

    def extract_vessel(self, metadata_url):
        meta = self.get_metadata(metadata_url)
        if (meta == None):
            return "N/A"

        return self.combine_if_list(meta.vessel)

    def extract_instrument(self, metadata_url):
        meta = self.get_metadata(metadata_url)
        if (meta == None):
            return "N/A"

        return self.combine_if_list(meta.instrument)

    def combine_if_list(self, value, separator=', '):
        return separator.join(value) if isinstance(value, list) else value


class TestMetadataCache(unittest.TestCase):
    def test_single_instrument(self):
        m = Mock()
        m.instrument = 'Kongsberg EM2040C'

        with patch.object(MetaDataCache, 'get_metadata', lambda x, y: m) as mock_method:
            meta_cache = MetaDataCache()
            result = meta_cache.extract_instrument('url')
            self.assertEqual('Kongsberg EM2040C', result)

    def test_multiple_instruments(self):
        m = Mock()
        m.instrument = ['Kongsberg EM2040C', 'Kongsberg EM3002D']

        with patch.object(MetaDataCache, 'get_metadata', lambda x, y: m) as mock_method:
            meta_cache = MetaDataCache()
            result = meta_cache.extract_instrument('url')
            self.assertEqual('Kongsberg EM2040C, Kongsberg EM3002D', result)


if __name__ == "__main__":
    meta_cache = MetaDataCache()
    # url = 'http://pid.geoscience.gov.au/dataset/ga/130301'
    url = 'http://pid.geoscience.gov.au/dataset/ga/74915'
    meta = meta_cache.get_metadata(url)
    start = meta_cache.extract_start(url)
    end = meta_cache.extract_end(url)
    logging.info(start)
    logging.info(end)
