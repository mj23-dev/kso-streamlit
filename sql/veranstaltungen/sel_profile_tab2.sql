select distinct
        wv.vollname_der_firma, wu.seite, wu.email, wu.telefonnummer, wu.rechtsform, wu.product_name_agg, wu.tatigkeitsbeschreibung, 
        wu.uns_mitg, wu.uns_mitg_maxd, wu.aktivitaten_id as last_akt_id, strftime(wu.akt_maxd, '%Y-%m-%d') || ' | ' || wu.akt_titel as akt_datum_titel,
        wu.juradr_land, wu.juradr_bundesland, wu.juradr_plz_ort, wu.juradr_strasse,
        wu.heaf, wu.uns_id, wu.hauptunternehmen_id, wv.aktivitaten_id, wv.datum_titel
from w_veranstaltung wv
inner join w_uns wu on wv.uns_id = wu.uns_id
where wv.aktivitaten_id = '{selected_id}'
and wv.fact = 'fact'
order by wv.vollname_der_firma