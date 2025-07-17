select wu.vollname_der_firma, 
		count(distinct wu.pers_id) over (partition by wu.uns_id) as cnt_pers,
		concat_ws(' ', wu.vorname, upper(wu.nachname)) as vor_nachname,
		wu.prsd, wu.vrst, wu.gnrl, wu.rchn, 
		wu.pos1, case when wu.pos2 != wu.pos1 then wu.pos2 else null end as pos2,
		wu.email, wu.juradr_bundesland, wu.juradr_full, wu.vorname, wu.nachname, wu.uns_id, wu.pers_id
  from (select wu.vollname_der_firma, 
		--		concat_ws(' ', wu.vorname, upper(wu.nachname)) as vor_nachname, 
				wu.vorname, wu.nachname,
				max(case when wu.pers_kategorie like '%Präsidium%' then 1 else 0 end) as prsd,
				max(case when wu.pers_kategorie like '%Vorstand%' then 1 else 0 end) as vrst,
				max(case when wu.pers_kategorie like '%Generalsekretär%' then 1 else 0 end) as gnrl,
				max(case when wu.pers_kategorie like '%Rechnungsprüfer%' then 1 else 0 end) as rchn,
				coalesce(min(wu.pers_position),'-') as pos1, coalesce(max(wu.pers_position),'-') as pos2,
				wu.email1 as email, wu.juradr_bundesland, wu.juradr_full, wu.uns_id, wu.pers_id
		  from (select wu.uns_id, wu.vollname_der_firma, wu.juradr_bundesland, wu.juradr_full, wlup.pers_id, 
						split_part(wlup.pers_position, '(', 1) as pers_kategorie,
						replace(split_part(wlup.pers_position, '(', 2),')','') as pers_position,
						wp.vorname, wp.nachname, wp.email1
				from main.w_uns wu
				left join (select * from main.w_links_uns_pers wlup 
							where current_date() between wlup.datum_von and wlup.datum_bis
							  --and wlup.uns_id like 'V0444913001%'
							) as wlup on wlup.uns_id = wu.uns_id
				left join main.w_pers wp on wp.pers_id = wlup.pers_id
				where wu.hauptunternehmen_id = 'V0444913001'
				--and wu.uns_id != 'V0444913001.000'
				--order by wu.uns_id, wlup.pers_id
				) wu
		group by wu.uns_id, wu.vollname_der_firma, wu.juradr_bundesland, wu.juradr_full, wu.pers_id, wu.vorname, wu.nachname, wu.email1
		) wu
where wu.uns_id not in ('V0444913001.000','V0444913001.010')
order by wu.uns_id, 4 desc, 5 desc, 6 desc, 7 desc,
		case when wu.pos1 = 'Präsident' then 1
			 when wu.pos1 = '1. Vizepräsident' then 2
			 when wu.pos1 = '2. Vizepräsident' then 3
			 when wu.pos1 = '3. Vizepräsident' then 4
			 when wu.pos1 = '4. Vizepräsident' then 5
			 when wu.pos1 = 'Generalsekretär' then 6
			 when wu.pos1 = 'Rechnungsprüfer' then 7
			 when wu.pos1 = 'Kassier' then 8
			 when wu.pos1 = 'Präsident' then 9
			 when wu.pos1 = 'Kassier Stellvertreter' then 10
		end, wu.nachname