select wp.vorname, wp.nachname, wp.pers_id, wp.pers_mitg, wp.pers_mitg_maxd,
	wp.anrede, wp.titel_vorne, wp.titel_hinten, 
	coalesce(wp.domain1, wp.domain2, wp.domain3, wp.domain4, wp.domain5, wp.domain6, wp.domain7, wp.domain8, '-') as domain,
	wp.telefonnummer, wp.geburtsdatum, wp.sprachen,
	wp.email1, wp.email2, wp.email3, wp.email4, wp.email5,
	wp.rechnungs_email1, wp.rechnungs_email2, wp.rechnungs_email3,
	wp.juradr_land, wp.juradr_bundesland, wp.adr_plz_ort, wp.strasse, wp.juradr_full,
	wp.akt_titel, wp.akt_maxd, wp.aktivitaten_id,
	coalesce(wu.cnt_uns,0) as cnt_uns, wu.vollname_der_firma_aggr, wu.kurzbezeichnung_aggr
from main.w_pers wp
left join (select wlup.pers_id, wlup.cnt_uns,
			string_agg(wlup.vollname_der_firma, ' | ') as vollname_der_firma_aggr,
			string_agg(wlup.kurzbezeichnung, ' | ') as kurzbezeichnung_aggr
		from (select wlup.pers_id, count(distinct wu.vollname_der_firma) over (partition by wlup.pers_id) as cnt_uns,
				case when wu.vollname_der_firma is not null then wu.vollname_der_firma || ' (' || wlup.uns_id || ')'
				end as vollname_der_firma,
				case when wu.kurzbezeichnung is not null then wu.kurzbezeichnung || ' (' || wlup.uns_id || ')'
				end as kurzbezeichnung
			from main.w_links_uns_pers wlup 
			left join main.w_uns wu on wlup.uns_id = wu.uns_id
			where current_date between wlup.datum_von and wlup.datum_bis
			group by wlup.pers_id, wlup.uns_id, wu.vollname_der_firma, wu.kurzbezeichnung
			) wlup
		group by wlup.pers_id, wlup.cnt_uns) as wu on wp.pers_id = wu.pers_id
order by coalesce(wp.domain1, wp.domain2, wp.domain3, wp.domain4, wp.domain5, wp.domain6, wp.domain7, wp.domain8), 
	wp.nachname, wp.vorname