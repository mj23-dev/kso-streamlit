select wlup.uns_id, wlup.pers_id, wp.vorname, wp.nachname,
	lower(concat_ws(';', wlup.email1, wlup.email2, wlup.email3, wlup.email4, wlup.email5)) as email,
	wlup.pers_kategorie, wlup.pers_position, wp.telefonnummer,
	wp.pers_mitg, wp.pers_mitg_maxd
from main.w_links_uns_pers wlup
left join main.w_pers wp on wlup.pers_id = wp.pers_id