-- Schéma de la base meteo_madagascar
-- Deux tables : les villes (peu de lignes, qui ne changent presque pas)
-- et les mesures météo (beaucoup de lignes, une par ville et par jour).

CREATE TABLE IF NOT EXISTS villes (
    id          SERIAL PRIMARY KEY,              -- identifiant unique, généré automatiquement
    nom         VARCHAR(100) NOT NULL UNIQUE,    -- UNIQUE : pas deux villes avec le même nom
    latitude    NUMERIC(8,5) NOT NULL,
    longitude   NUMERIC(8,5) NOT NULL
);

CREATE TABLE IF NOT EXISTS meteo_quotidienne (
    ville_id       INTEGER NOT NULL REFERENCES villes(id),  -- clé étrangère : la ville doit exister
    date           DATE NOT NULL,
    temp_max       NUMERIC(4,1) NOT NULL,
    temp_min       NUMERIC(4,1) NOT NULL,
    pluie_mm       NUMERIC(5,1) NOT NULL DEFAULT 0,
    temp_moy       NUMERIC(4,1) NOT NULL,
    jour_pluvieux  BOOLEAN NOT NULL,
    PRIMARY KEY (ville_id, date),                           -- une seule ligne par ville et par jour
    CHECK (temp_min <= temp_max),                           -- la base refuse les données absurdes
    CHECK (pluie_mm >= 0)
);

CREATE INDEX IF NOT EXISTS meteo_date_idx ON meteo_quotidienne (date);
