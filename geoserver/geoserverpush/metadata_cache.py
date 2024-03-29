import logging
import os
import unittest
from unittest.mock import patch, Mock
from xml.etree import ElementTree

import boto3
import requests
from botocore.exceptions import ClientError

from custom_iso_parser import CustomIsoParser


class MetaDataCache():
    def __init__(self):
        self.s3 = boto3.client('s3')

        self.metadata = {}
        self.zip_file_urls = {}

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
            metadata_response = requests.get(metadata_url + "?_format=text/xml&_view=ISO19115", timeout=5)

            tree = ElementTree.fromstring(metadata_response.text)
            metadata = tree.find(".//mdb:MD_Metadata", namespaces={"mdb": "http://standards.iso.org/iso/19115/-3/mdb/1.0"})

            if (metadata_response.ok and metadata):
                iso_from_file = CustomIsoParser(ElementTree.tostring(metadata))
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
        return abstract + '<br>\n\n' + metadata_url

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

    def get_zip_file_url(self, file):
        if file in self.zip_file_urls:
            return self.zip_file_urls[file]

        zip_file_url = self.create_and_validate_zip_file_url(file)
        self.zip_file_urls[file] = zip_file_url
        return zip_file_url

    def create_and_validate_zip_file_url(self, file):
        key = os.environ["FILES_PREFIX"] + file

        try:
            self.s3.head_object(Bucket=os.environ['FILES_BUCKET'], Key=key)
            return f'https://{os.environ["FILES_BUCKET"]}/{key}'
        except ClientError as e:
            if e.response['ResponseMetadata']['HTTPStatusCode'] == 404:
                logging.warning('Survey zip file does not exist [bucket=%s, key=%s]', os.environ['FILES_BUCKET'], key)
            else:
                logging.exception('Failed to determine whether survey zip file exists')

        return ''

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
