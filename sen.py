import scrapy
import re

from crawlers.utils import SpiderBase
from crawlers.utils.group_alarm import catch_except
from jinja2 import Template


def minimal_regularity(pattern, string):
    comp = re.compile(pattern, re.S)
    return re.findall(comp, string)


class BtcMVRVSpider(SpiderBase):
    name = 'idx-btc-mvrv'
    url = 'https://charts.woobull.com/bitcoin-mvrv-ratio/'

    def start_requests(self):
        # error_back method is defined in SpiderBase
        yield scrapy.Request(url=self.url, errback=self.error_back)

    # Exceptions must be handled, only need to be declared, and the processing logic system has been processed uniformly
    @catch_except
    def parse(self, response, **kwargs):
        string = response.text
        for pattern in ['mvrv = .*?}', 'y:.*?]', r'\[.*\]']:
            # Get the desired data from html
            string = minimal_regularity(pattern, string)[0]
        btc_mv_rv = eval(string)[-1]
        params = {
            'mv_rv': round(btc_mv_rv, 2)
        }
        print(Template(self.alert_en_template()).render(params))
        print(Template(self.alert_cn_template()).render(params))

    # must be declare
    def alert_en_template(self):
        return """According to KingData monitoring, BTC current MVRV ratio is {{mv_rv}}，{% if mv_rv < 1 %}theoretically the price is at bottom, marking late stage bear market accumulations.{% endif %}{% if mv_rv > 3.7 %} theoretically the price is at top, signaling late stage bull cycles.{% endif %}{% if 1<= mv_rv <= 3.7 %}Theoretically, MVRV values over '3.7' indicated price top and values below '1' indicated price bottom.{% endif %}
 (The above content is for your reference only and does not constitute investment advice. Invest at your own risk.)  """
