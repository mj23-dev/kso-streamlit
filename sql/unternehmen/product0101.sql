select wup.product_name, wu.vollname_der_firma, 
		wu.seite, wu.email, wu.telefonnummer, wu.rechtsform,
		wu.juradr_land, wu.juradr_bundesland, wu.juradr_plz_ort, wu.juradr_strasse, wu.juradr_full,
		wu.product_name_agg, wu.tatigkeitsbeschreibung, wu.registrierungsstatus,
		wu.uns_mitg, wu.uns_mitg_maxd, wu.aktivitaten_id, wu.akt_titel, wu.akt_maxd,
		wu.heaf, wu.hauptunternehmen_id, wu.uns_id
from w_uns wu
inner join w_uns_prod wup on wup.uns_id = wu.uns_id
order by wup.product_name, wu.vollname_der_firma