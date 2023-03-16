from datetime import date
from datetime import timedelta
from math import floor
from jours_feries_france import JoursFeries
import pandas as pd
def calculer_conge_accueil_enfant(jour:int, mois:int, annee:int=2023, jours_naissances:int = 3, jours_conge:int = 25, cp_par_mois:float=2.08,rtt_par_an:int=20, pct_avance_conges:float=0.25, 
                                  date_debut_calcul_conges:date=date.today().replace(day=1, month=1), 
                                  conges_cumules_avant:int=0, fin_du_contrat:date=date.today().replace(month=12).replace(day=31)):
    """ Cette fonction aide à calculer la date de retour de congé paternité / accueil d'enfant pour la personne en couple avec la mère. Elle prend en compte les arguments suivants :
        - jour (int) : jour de naissance.
        - mois (int) : mois de naissance.
        - annee (int) : année de naissance.
        - jours_naissance (int) : La loi établi 3 jours ouvrés de naissance en ce moment, à compter à partir du jour suivant de l'accouchement.
        - conge_paternite (int) : Nombre de jours que la personne veut prendre comme congé d'accueil de l'enfant. Par défaut : La valeur maximale prévue par la loi : 25. Espérons que ce soit augmenté bientôt !
        - cp_par_mois (float) : Le nombre de congé payés acquis par la personne, par mois. Par défaut : 2.08.
        - rtt_par_an (int) : Si la personne en a, nombre de rtt acquis par an. Par défaut, 20. Peut être 0.
        - pct_avance_conges (float) : Pourcentage des congés payés non acquis encore qui peut être avancé par l'entreprise. Par défaut : 0.25.
        - date_debut_calcul_conges (datetime.date) : Par défaut, le 1er janvier de l'année en cours. Elle peut être modifiée avec la date de début du contrat.
        - conges_cumules_avant (int) : Pour les chanceux·ses qui ont gardé des congés de l'année précédente, ils peuvent être ajoutés ici. Par défaut : 0.
        - fin_du_contrat (datetime.date) : Par défaut : le 31 décembre de l'année en cours. C'est la date de fin de contrat pour les CDD si celle-ci arrive avant la fin de l'année. Cette date est prise en compte pour 
            calculer les congés acquis.
        
        Pour l'instant, cette fonctionne marche parfaitement pour les contrats qui vont du 1er d'un mois jusqu'au dernier d'un autre mois. Pour d'autres cas de figure, il faudra attendre des versions futures.
    """    
    naissance = date(int(annee),int(mois),int(jour))
    date_apres_conge_paternite = naissance + timedelta(days=1) + timedelta(days=jours_naissances) + timedelta(days=jours_conge)
    for i in pd.date_range(naissance + timedelta(days=1), naissance+timedelta(days=jours_naissances)):
        if i.weekday() == 5 or i.weekday()==6 or i.date() in list(JoursFeries.for_year(date_apres_conge_paternite.year).values()):
            date_apres_conge_paternite += timedelta(days=1)
    date_apres_conge_paternite.weekday()
    if date_apres_conge_paternite.weekday()==5:
        date_apres_conge_paternite += timedelta(days=2)
    elif date_apres_conge_paternite.weekday()==6:
        date_apres_conge_paternite += timedelta(days=1)
    conges_payes = ((date_apres_conge_paternite+timedelta(days=1)).month - date_debut_calcul_conges.month)*cp_par_mois+conges_cumules_avant
    rtt = ((date_apres_conge_paternite+timedelta(days=1)).month - date_debut_calcul_conges.month)*(rtt_par_an/6)
    avance_cp = (fin_du_contrat.month+1 - (date_apres_conge_paternite+timedelta(days=1)).month)*cp_par_mois*pct_avance_conges
    avance_rtt = (fin_du_contrat.month+1 - (date_apres_conge_paternite+timedelta(days=1)).month)*(rtt_par_an/6)*pct_avance_conges
    total_conges = conges_payes + rtt + avance_cp + avance_rtt
    date_apres_premiers_conges = date_apres_conge_paternite + timedelta(days = floor(total_conges)) 
    dates_a_verifier = pd.date_range(date_apres_conge_paternite, date_apres_premiers_conges).to_list()
    while len(dates_a_verifier)>0:
        for i in dates_a_verifier:
            if i.weekday() == 5 or i.weekday()==6 or i.date() in list(JoursFeries.for_year(date_apres_premiers_conges.year).values()):
                date_apres_premiers_conges += timedelta(days=1)
                dates_a_verifier.append(pd.to_datetime(date_apres_premiers_conges))
            dates_a_verifier.remove(i)
    if date_apres_premiers_conges.month != date_apres_conge_paternite.month:
        conges_payes = ((date_apres_premiers_conges+timedelta(days=1)).month-date_debut_calcul_conges.month)*cp_par_mois+conges_cumules_avant
        rtt = ((date_apres_premiers_conges+timedelta(days=1)).month-date_debut_calcul_conges.month)*(rtt_par_an/6)
        avance_cp = (fin_du_contrat.month+1 - (date_apres_premiers_conges+timedelta(days=1)).month)*cp_par_mois*pct_avance_conges
        avance_rtt = (fin_du_contrat.month+1 - (date_apres_premiers_conges+timedelta(days=1)).month)*(rtt_par_an/6)*pct_avance_conges
        total_conges = conges_payes + rtt + avance_cp + avance_rtt

    date_apres_conges = date_apres_conge_paternite + timedelta(days = floor(total_conges)) 
    dates_a_verifier = pd.date_range(date_apres_conge_paternite, date_apres_conges).to_list()
    while len(dates_a_verifier)>0:
        for i in dates_a_verifier:
            if i.weekday() == 5 or i.weekday()==6 or i.date() in list(JoursFeries.for_year(date_apres_conges.year).values()):
                date_apres_conges += timedelta(days=1)
                dates_a_verifier.append(pd.to_datetime(date_apres_conges))
            dates_a_verifier.remove(i)
    return f"Si le bébé est né le {naissance.strftime('%d/%m/%Y')}, alors le retour au travail serait le {date_apres_conges.strftime('%d/%m/%Y')}, avec {floor(total_conges)} jours de congés pris et une durée totale de congé de \
        {(date_apres_conges - naissance).days} jours calendaires. Il me resteraient {floor(rtt_par_an+cp_par_mois*12)-floor(total_conges)} jours de congés."