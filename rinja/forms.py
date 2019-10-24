from django import forms


class ApiStocksListingRequestSchema(forms.Form):
    watchlist = forms.BooleanField(required=False, initial=False)
