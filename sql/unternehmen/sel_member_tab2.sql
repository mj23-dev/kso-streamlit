SELECT distinct wv.*
  from (select wv.datum_titel, case when wv.agenda_link = '-' then null else wv.agenda_link end as agenda_link, 
                wv.format, coalesce(wv.bundesland,'-') as bundesland, wv.akt_org, wv.akt_spn,
                wv.adr_full, wv.aktivitaten_id
            from main.w_veranstaltung wv 
            group by wv.datum_titel, wv.aktivitaten_id, wv.agenda_link, wv.format, wv.datum_bis_year, 
                    wv.bundesland, wv.akt_org, wv.akt_spn, wv.adr_full
        ) wv
INNER JOIN main.w_veranstaltung wv2 on wv.aktivitaten_id = wv2.aktivitaten_id
WHERE wv2.uns_id = '{selected_uns_id}'
ORDER BY 1 desc