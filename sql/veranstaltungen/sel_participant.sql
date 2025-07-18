select wv.datum_titel, case when wv.agenda_link = '-' then null else wv.agenda_link end as agenda_link, 
	count(distinct case when wv.plan = 'plan' then wv.pers_id else null end) as cntp_pers,
	count(distinct case when wv.fact = 'fact' then wv.pers_id else null end) as cntf_pers, 
	count(distinct case when wv.fact = 'fact' then wv.uns_id else null end) as cnt_uns,
	wv.datum_bis_year, wv.format, coalesce(wv.bundesland,'-') as bundesland, wv.akt_org, wv.akt_spn,
	wv.aktivitaten_id, wv.datum_bis, wv.titel, wv.adr_full
from main.w_veranstaltung wv
group by wv.datum_titel, wv.aktivitaten_id, wv.agenda_link, wv.format, wv.datum_bis_year, 
		wv.bundesland, wv.akt_org, wv.akt_spn, wv.datum_bis, wv.titel, wv.adr_full
order by wv.datum_titel desc