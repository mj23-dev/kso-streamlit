SELECT distinct 
        wu.vollname_der_firma, wlup.pers_position, wu.uns_id, 
        case when wu.seite not like 'http%' and wu.seite not like 'www%' then null else wu.seite end as seite, 
        wu.email, wu.telefonnummer, 
        wu.rechnungsadr_land, wu.rechnungsadr_bundesland, wu.rechnungsadr_plz_ort, 
        wu.rechtsform, 
        wu.code5 as onace_code5, wu.onace_sh_de1, wu.onace_sh_de2, wu.onace_sh_de3, wu.onace_sh_de4, wu.onace_sh_de5,
        wu.product_name_agg, wu.tatigkeitsbeschreibung,
        wu.uns_mitg, wu.uns_mitg_maxd, wu.aktivitaten_id, wu.akt_titel, wu.akt_maxd,
        wu.heaf, wu.hauptunternehmen_id, wu.kurzbezeichnung, wu.rechnungsadr_full, wu.registrierungsstatus, wu.compass_id,
        wp.pers_id
FROM main.w_pers wp
INNER join main.w_links_uns_pers wlup on wlup.pers_id = wp.pers_id
INNER join main.w_uns wu on wu.uns_id = wlup.uns_id
WHERE wp.pers_id = '{selected_pers_id}'
ORDER BY 1,2