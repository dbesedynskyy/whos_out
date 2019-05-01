import os
import json
import random

def loadQuoteFile(quoteFile = 'quotes.json'):
    quote_fname = os.path.join(os.path.dirname(__file__), quoteFile)
    with open(quote_fname) as json_data:
        return json.load(json_data)

class QuoteHelper():
    _quotes_data = loadQuoteFile()["data"]

    @classmethod
    def getQuote(cls):
        index = random.randint(0, len(cls._quotes_data))
        return cls._quotes_data[index]