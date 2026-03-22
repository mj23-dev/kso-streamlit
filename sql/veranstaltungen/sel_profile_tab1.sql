SELECT wv.vorname, wv.nachname, wv.anrede, wv.titel_vorne, wv.titel_hinten, wv.pers_rolle, wv.kso_pers_position,
        concat_ws('; ', wv.email1, wv.email2, wv.email3) as email,
        wv.pers_mitg, wv.pers_mitg_maxd, 
        wv.vollname_der_firma, wv.uns_mitg, wv.uns_mitg_maxd,
        wu.product_name_agg,
        wv.uns_id, wv.pers_id, wv.aktivitaten_id, wv.datum_titel
FROM w_veranstaltung wv
LEFT JOIN w_uns wu ON wv.uns_id = wu.uns_id
WHERE wv.aktivitaten_id = '{selected_id}'
and wv.fact = 'fact'
and not(wv.uns_id is null and wv.pers_id is null)
ORDER BY wv.vollname_der_firma, wv.nachname, wv.vorname