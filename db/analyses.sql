-- Requêtes d'analyse sur la base meteo_madagascar
-- Chaque requête répond à une question précise. Exécutez-les une par une.

-- 1) Quelle est la température moyenne de chaque ville ?
SELECT v.nom, ROUND(AVG(m.temp_moy), 1) AS temp_moyenne
FROM meteo_quotidienne m
JOIN villes v ON v.id = m.ville_id
GROUP BY v.nom
ORDER BY temp_moyenne DESC;

-- 2) Où a-t-il le plus plu ? (pluie totale et nombre de jours pluvieux)
SELECT v.nom,
       SUM(m.pluie_mm)              AS pluie_totale_mm,
       SUM(m.jour_pluvieux::int)    AS jours_pluvieux
FROM meteo_quotidienne m
JOIN villes v ON v.id = m.ville_id
GROUP BY v.nom
ORDER BY pluie_totale_mm DESC;

-- 3) Quel a été le jour le plus chaud de chaque ville ?
SELECT DISTINCT ON (v.nom) v.nom, m.date, m.temp_max
FROM meteo_quotidienne m
JOIN villes v ON v.id = m.ville_id
ORDER BY v.nom, m.temp_max DESC;

-- 4) Quelle ville a les plus grands écarts de température entre le jour et la nuit ?
SELECT v.nom, ROUND(AVG(m.temp_max - m.temp_min), 1) AS amplitude_moyenne
FROM meteo_quotidienne m
JOIN villes v ON v.id = m.ville_id
GROUP BY v.nom
ORDER BY amplitude_moyenne DESC;

-- 5) Classement des villes par pluie pour chaque jour (fonction de fenêtre RANK)
SELECT m.date, v.nom, m.pluie_mm,
       RANK() OVER (PARTITION BY m.date ORDER BY m.pluie_mm DESC) AS rang_du_jour
FROM meteo_quotidienne m
JOIN villes v ON v.id = m.ville_id
ORDER BY m.date, rang_du_jour;
