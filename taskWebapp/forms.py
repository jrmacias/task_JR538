from django import forms


class DsSearchForm(forms.Form):
    ds_accession = forms.CharField(
        label=False,
        help_text="Dataset accession: i.e.: MTBLS1 | ST000025 | MTBKS93",
        max_length=100,
        widget=forms.TextInput(attrs={'class': "form-control"}),
    )
