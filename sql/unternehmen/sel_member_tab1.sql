SELECT wlup.pers_id, wp.vorname, wp.nachname, 
       concat_ws('; ', wlup.email1, wlup.email2, wlup.email3, wlup.email4, wlup.email5) as email,
       wlup.pers_kategorie, wlup.pers_position, wp.telefonnummer, 
       wp.pers_mitg, wp.pers_mitg_maxd, wp.aktivitaten_id, wp.akt_titel, wp.akt_maxd,
       wu.kurzbezeichnung, wu.uns_id
FROM w_uns wu
INNER JOIN main.w_links_uns_pers wlup ON wu.uns_id = wlup.uns_id
INNER JOIN main.w_pers wp ON wlup.pers_id = wp.pers_id
WHERE wu.uns_id = '{selected_uns_id}'
ORDER BY case when wlup.pers_kategorie = 'MG_Ord_Vertr' then 1 else 2 end, 3,2