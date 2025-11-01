
CREATE TABLE IF NOT EXISTS historical_matches (
    id SERIAL PRIMARY KEY,
    match_id BIGINT UNIQUE NOT NULL,
    date_utc TIMESTAMP NOT NULL,
    season VARCHAR(20) NOT NULL,
    league_id INTEGER,
    league_name VARCHAR(100),
    competition_id INTEGER,
    
    home_id INTEGER NOT NULL,
    away_id INTEGER NOT NULL,
    home_name VARCHAR(100) NOT NULL,
    away_name VARCHAR(100) NOT NULL,
    
    result VARCHAR(10) NOT NULL,
    goals_home INTEGER NOT NULL,
    goals_away INTEGER NOT NULL,
    
    odds_ft_1 DECIMAL(6,2),
    odds_ft_x DECIMAL(6,2),
    odds_ft_2 DECIMAL(6,2),
    odds_btts_yes DECIMAL(6,2),
    odds_btts_no DECIMAL(6,2),
    odds_over25 DECIMAL(6,2),
    odds_under25 DECIMAL(6,2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    data_source VARCHAR(50) DEFAULT 'footystats',
    
    CONSTRAINT valid_result CHECK (result IN ('home', 'draw', 'away'))
);

CREATE INDEX IF NOT EXISTS idx_historical_matches_date ON historical_matches(date_utc);
CREATE INDEX IF NOT EXISTS idx_historical_matches_league ON historical_matches(league_id);
CREATE INDEX IF NOT EXISTS idx_historical_matches_teams ON historical_matches(home_id, away_id);
CREATE INDEX IF NOT EXISTS idx_historical_matches_season ON historical_matches(season);

CREATE TABLE IF NOT EXISTS match_features (
    id SERIAL PRIMARY KEY,
    match_id BIGINT UNIQUE NOT NULL,
    
    home_form_5 DECIMAL(5,3),
    home_form_10 DECIMAL(5,3),
    home_goals_for_avg DECIMAL(5,2),
    home_goals_against_avg DECIMAL(5,2),
    home_elo_rating DECIMAL(8,2),
    home_days_rest INTEGER,
    home_matches_last_14d INTEGER,
    
    away_form_5 DECIMAL(5,3),
    away_form_10 DECIMAL(5,3),
    away_goals_for_avg DECIMAL(5,2),
    away_goals_against_avg DECIMAL(5,2),
    away_elo_rating DECIMAL(8,2),
    away_days_rest INTEGER,
    away_matches_last_14d INTEGER,
    
    market_prob_home DECIMAL(5,3),
    market_prob_draw DECIMAL(5,3),
    market_prob_away DECIMAL(5,3),
    
    is_derby BOOLEAN DEFAULT FALSE,
    h2h_home_wins_last3 INTEGER,
    h2h_draws_last3 INTEGER,
    h2h_away_wins_last3 INTEGER,
    
    features_version VARCHAR(20) DEFAULT 'v1.0',
    computed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_match_features_match ON match_features(match_id);

CREATE TABLE IF NOT EXISTS ml_predictions (
    id SERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL,
    
    model_version VARCHAR(50) NOT NULL,
    predicted_prob_home DECIMAL(5,3) NOT NULL,
    predicted_prob_draw DECIMAL(5,3) NOT NULL,
    predicted_prob_away DECIMAL(5,3) NOT NULL,
    
    calibrated_prob_home DECIMAL(5,3),
    calibrated_prob_draw DECIMAL(5,3),
    calibrated_prob_away DECIMAL(5,3),
    
    actual_result VARCHAR(10),
    
    log_loss DECIMAL(8,4),
    brier_score DECIMAL(8,4),
    
    predicted_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_actual_result CHECK (actual_result IN ('home', 'draw', 'away', NULL))
);

CREATE INDEX IF NOT EXISTS idx_ml_predictions_match ON ml_predictions(match_id);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_model ON ml_predictions(model_version);

CREATE TABLE IF NOT EXISTS team_season_stats (
    id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL,
    season VARCHAR(20) NOT NULL,
    competition_id INTEGER,
    
    matches_played INTEGER,
    wins INTEGER,
    draws INTEGER,
    losses INTEGER,
    goals_for INTEGER,
    goals_against INTEGER,
    goal_difference INTEGER,
    
    home_matches INTEGER,
    home_wins INTEGER,
    home_goals_for INTEGER,
    home_goals_against INTEGER,
    away_matches INTEGER,
    away_wins INTEGER,
    away_goals_for INTEGER,
    away_goals_against INTEGER,
    
    fetched_at TIMESTAMP DEFAULT NOW(),
    data_json JSONB,
    
    UNIQUE(team_id, season, competition_id)
);

CREATE INDEX IF NOT EXISTS idx_team_season_stats_team ON team_season_stats(team_id, season);

CREATE TABLE IF NOT EXISTS team_elo_ratings (
    id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL,
    date_utc TIMESTAMP NOT NULL,
    elo_rating DECIMAL(8,2) NOT NULL,
    
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(team_id, date_utc)
);

CREATE INDEX IF NOT EXISTS idx_team_elo_team_date ON team_elo_ratings(team_id, date_utc DESC);

CREATE OR REPLACE VIEW ml_training_data AS
SELECT 
    hm.match_id,
    hm.date_utc,
    hm.season,
    hm.league_name,
    hm.home_name,
    hm.away_name,
    hm.result,
    hm.goals_home,
    hm.goals_away,
    mf.home_form_5,
    mf.home_form_10,
    mf.home_goals_for_avg,
    mf.home_goals_against_avg,
    mf.home_elo_rating,
    mf.away_form_5,
    mf.away_form_10,
    mf.away_goals_for_avg,
    mf.away_goals_against_avg,
    mf.away_elo_rating,
    mf.market_prob_home,
    mf.market_prob_draw,
    mf.market_prob_away,
    mp.predicted_prob_home,
    mp.predicted_prob_draw,
    mp.predicted_prob_away,
    mp.log_loss,
    mp.brier_score
FROM historical_matches hm
LEFT JOIN match_features mf ON hm.match_id = mf.match_id
LEFT JOIN ml_predictions mp ON hm.match_id = mp.match_id
ORDER BY hm.date_utc DESC;

COMMENT ON TABLE historical_matches IS 'Partidos históricos con resultados y cuotas para entrenamiento ML';
COMMENT ON TABLE match_features IS 'Features calculadas por partido (sin data leakage) para ML';
COMMENT ON TABLE ml_predictions IS 'Predicciones del modelo ML para validación y monitoreo';
COMMENT ON TABLE team_season_stats IS 'Estadísticas de equipos por temporada (cache de FootyStats API)';
COMMENT ON TABLE team_elo_ratings IS 'Ratings Elo históricos de equipos para feature engineering';
