from django import forms


class DonneesForm(forms.Form):

    # Demandes par région
    demande_R1 = forms.IntegerField(label='R1', min_value=0)
    demande_R2 = forms.IntegerField(label='R2', min_value=0)
    demande_R3 = forms.IntegerField(label='R3', min_value=0)
    demande_R4 = forms.IntegerField(label='R4', min_value=0)

    # Capacités des centres
    capacite_C1 = forms.IntegerField(label='C1', min_value=0)
    capacite_C2 = forms.IntegerField(label='C2', min_value=0)
    capacite_C3 = forms.IntegerField(label='C3', min_value=0)

    # Coûts C1
    cout_C1_R1 = forms.FloatField(label='C1 - R1', min_value=0)
    cout_C1_R2 = forms.FloatField(label='C1 - R2', min_value=0)
    cout_C1_R3 = forms.FloatField(label='C1 - R3', min_value=0)
    cout_C1_R4 = forms.FloatField(label='C1 - R4', min_value=0)

    # Coûts C2
    cout_C2_R1 = forms.FloatField(label='C2 - R1', min_value=0)
    cout_C2_R2 = forms.FloatField(label='C2 - R2', min_value=0)
    cout_C2_R3 = forms.FloatField(label='C2 - R3', min_value=0)
    cout_C2_R4 = forms.FloatField(label='C2 - R4', min_value=0)

    # Coûts C3
    cout_C3_R1 = forms.FloatField(label='C3 - R1', min_value=0)
    cout_C3_R2 = forms.FloatField(label='C3 - R2', min_value=0)
    cout_C3_R3 = forms.FloatField(label='C3 - R3', min_value=0)
    cout_C3_R4 = forms.FloatField(label='C3 - R4', min_value=0)