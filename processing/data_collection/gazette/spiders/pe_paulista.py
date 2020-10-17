import chompjs
import dateparser

from base64 import b64encode
from datetime import datetime
from gazette.items import Gazette
from gazette.spiders.base import BaseGazetteSpider

from scrapy import Request, Spider


class PePaulistaSpider(BaseGazetteSpider):
    name = 'pe_paulista'
    allowed_domains = ['dosp.com.br']

    DATE_FORMAT = '%Y-%m-%d'
    GAZETTE_URL = 'https://dosp.com.br/api/index.php/dioe.js/3281'
    PDF_URL = 'https://dosp.com.br/exibe_do.php?i={}'
    TERRITORY_ID = '2610707'

    EL_DATA = 'data'
    EL_EDITION_NUMBER = 'edicao_do'
    EL_EXTRA = 'flag_extra'
    EL_JORNAL_ID = 'iddo'

    def start_requests(self):
        yield Request(self.GAZETTE_URL)

    def parse(self, response):
        response = chompjs.parse_js_object(response.text)

        for element in response.get('data'):
            date = self.extract_date(element)
            url = self.extract_url(element)
            edition_number = self.extract_edition_number(element)
            is_extra_edition = self.extract_extra_edition(element)
            print()

            yield Gazette(
                date=date,
                file_urls=[url],
                edition_number=edition_number,
                is_extra_edition=is_extra_edition,
                territory_id=self.TERRITORY_ID,
                power='executive_legislature',
                scraped_at=datetime.utcnow(),
            )

    def extract_date(self, element):
        journal_date = element.get(self.EL_DATA)

        return dateparser.parse(
            date_string=journal_date, 
            date_formats=[self.DATE_FORMAT], 
            languages=['pt']

        ).date()

    def extract_edition_number(self, element):
        return element.get(self.EL_EDITION_NUMBER)

    def extract_extra_edition(self, element):
        return bool(element.get(self.EL_EXTRA))

    def extract_url(self, element):
        jornal_id = str(element.get(self.EL_JORNAL_ID)).encode('ascii')
        pdf_id = b64encode(jornal_id).decode('ascii')
        return self.PDF_URL.format(pdf_id)