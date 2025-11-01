-- Create predicciones_historicas table for shared storage between scheduler and bot

CREATE TABLE IF NOT EXISTS predicciones_historicas (
    id BIGSERIAL PRIMARY KEY,
    event_date DATE NOT NULL,
    kickoff_at TIMESTAMPTZ,
    match_id TEXT,
    league_id INT,
    league_name TEXT NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    market_code TEXT NOT NULL,
    selection TEXT NOT NULL,
    odds NUMERIC(6,2) NOT NULL,
    stake NUMERIC(4,1) NOT NULL,
    confidence NUMERIC(5,2) NOT NULL,
    expected_value NUMERIC(6,3) NOT NULL,
    reason TEXT,
    status TEXT DEFAULT 'pendiente' CHECK (status IN ('pendiente', 'acierto', 'fallo', 'void', 'cancelado')),
    result_payload JSONB,
    resolved_at TIMESTAMPTZ,
    telegram_message_id BIGINT,
    telegram_chat_id BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (match_id, market_code, selection, event_date)
);

CREATE INDEX IF NOT EXISTS idx_predicciones_status_date ON predicciones_historicas(status, event_date);
CREATE INDEX IF NOT EXISTS idx_predicciones_event_date ON predicciones_historicas(event_date DESC);
CREATE INDEX IF NOT EXISTS idx_predicciones_league ON predicciones_historicas(league_name, event_date);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_predicciones_updated_at BEFORE UPDATE
    ON predicciones_historicas FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE predicciones_historicas IS 'Historial de predicciones compartido entre scheduler y bot';
COMMENT ON COLUMN predicciones_historicas.match_id IS 'ID del partido en FootyStats API';
COMMENT ON COLUMN predicciones_historicas.market_code IS 'Código del mercado (btts, over_25, under_25, corners_95, etc)';
COMMENT ON COLUMN predicciones_historicas.selection IS 'Selección específica (Sí/No, Over/Under, etc)';
COMMENT ON COLUMN predicciones_historicas.status IS 'Estado: pendiente, acierto, fallo, void, cancelado';
