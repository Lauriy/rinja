from modeltranslation.translator import translator, TranslationOptions

from rinja.models import Stock


class StockTranslationOptions(TranslationOptions):
    fields = ('name', 'issuer')


translator.register(Stock, StockTranslationOptions)
