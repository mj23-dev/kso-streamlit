SELECT case when wv.fact = 'fact' then '+' else 'missing' end as part, 
        wv.vorname, wv.nachname, 
        wv.anrede, wv.titel_vorne, wv.titel_hinten, wv.pers_rolle, wv.kso_pers_position,
        concat_ws('; ', wv.email1, wv.email2, wv.email3) as email,
        wv.pers_mitg, wv.pers_mitg_maxd, 
        wv.vollname_der_firma, wv.uns_mitg, wv.uns_mitg_maxd,
        wu.product_name_agg,
        wv.uns_id, wv.pers_id, wv.aktivitaten_id, wv.datum_titel
FROM main.w_veranstaltung wv
LEFT JOIN main.w_uns wu ON wv.uns_id = wu.uns_id
WHERE wv.aktivitaten_id = '{selected_id}'
and not(wv.uns_id is null and wv.pers_id is null)
ORDER BY 1, wv.vollname_der_firma, wv.nachname, wv.vorname