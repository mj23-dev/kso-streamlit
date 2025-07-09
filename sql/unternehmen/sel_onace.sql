select wu.onace_sh_de1, wu.onace_sh_de2, wu.onace_sh_de3, wu.onace_sh_de4, wu.onace_sh_de5, wu.code5 as onace_code5,
	1 as cnt_uns, wu.vollname_der_firma, wu.uns_id, wu.cnt_pers, 
	case when wu.seite not like 'http%' and wu.seite not like 'www%' then null else wu.seite end as seite, 
	wu.email, wu.telefonnummer, 
	wu.rechnungsadr_land, wu.rechnungsadr_bundesland, wu.rechnungsadr_plz_ort, 
	wu.rechtsform, 
	wu.product_name_agg, wu.tatigkeitsbeschreibung,
	wu.uns_mitg, wu.uns_mitg_maxd, wu.aktivitaten_id, wu.akt_titel, wu.akt_maxd,
	wu.heaf, wu.hauptunternehmen_id, wu.kurzbezeichnung, wu.rechnungsadr_full, wu.registrierungsstatus, wu.compass_id
from main.w_uns wu
where wu.code5 is not null