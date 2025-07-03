select wu.uns_id, wu.vollname_der_firma, wu.seite, wu.email, wu.telefonnummer, wu.rechtsform,
		wu.juradr_land, wu.juradr_bundesland, wu.juradr_plz_ort, wu.juradr_strasse,
		wu.product_name_agg, wu.tatigkeitsbeschreibung, wu.registrierungsstatus,
		wu.uns_mitg, wu.uns_mitg_maxd, wu.aktivitaten_id, wu.akt_titel, wu.akt_maxd,
		wu.heaf, wu.hauptunternehmen_id
from main.w_uns wu