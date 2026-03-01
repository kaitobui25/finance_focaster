-- ============================================================
-- Finance Forecaster — PostgreSQL Schema
-- Version: 1.0 | 2026-03-01
-- Database: finance_forecaster | Owner: forecaster
-- ============================================================

-- ============================================================
-- 1. INSTRUMENTS — Master data cho symbols được track
-- ============================================================
CREATE TABLE IF NOT EXISTS instruments (
    id              SERIAL PRIMARY KEY,
    symbol          VARCHAR(30) UNIQUE NOT NULL,
    name            VARCHAR(200) NOT NULL,
    asset_type      VARCHAR(30) NOT NULL,
    exchange        VARCHAR(50),
    currency        VARCHAR(10) DEFAULT 'JPY',
    sector          VARCHAR(100),
    is_active       BOOLEAN DEFAULT TRUE,
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 2. ARTICLES — Bài báo từ RSS feeds
-- ============================================================
CREATE TABLE IF NOT EXISTS articles (
    id              SERIAL PRIMARY KEY,
    title           TEXT NOT NULL,
    link            TEXT UNIQUE NOT NULL,
    source          VARCHAR(100) NOT NULL,
    category        VARCHAR(50) DEFAULT 'general',
    language        VARCHAR(10) DEFAULT 'en',
    published_at    TIMESTAMPTZ,
    content         TEXT DEFAULT '',
    summary         TEXT DEFAULT '',
    keywords        JSONB DEFAULT '[]'::jsonb,
    is_processed    BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_articles_published ON articles(published_at DESC);
CREATE INDEX idx_articles_unprocessed ON articles(is_processed) WHERE is_processed = FALSE;
CREATE INDEX idx_articles_source ON articles(source);
CREATE INDEX idx_articles_category ON articles(category);
CREATE INDEX idx_articles_keywords ON articles USING GIN(keywords);

-- ============================================================
-- 3. REPORTS — Báo cáo daily digest
-- ============================================================
CREATE TABLE IF NOT EXISTS reports (
    id              SERIAL PRIMARY KEY,
    report_date     DATE NOT NULL,
    report_type     VARCHAR(20) NOT NULL,
    content         TEXT NOT NULL,
    market_sentiment VARCHAR(20),
    article_count   INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_reports_date ON reports(report_date DESC, report_type);

-- ============================================================
-- 4. MARKET_SNAPSHOTS — Giá thị trường
-- ============================================================
CREATE TABLE IF NOT EXISTS market_snapshots (
    id              SERIAL PRIMARY KEY,
    instrument_id   INTEGER NOT NULL REFERENCES instruments(id),
    price_open      DECIMAL(15,4),
    price_close     DECIMAL(15,4),
    price_high      DECIMAL(15,4),
    price_low       DECIMAL(15,4),
    change_pct      DECIMAL(8,4),
    volume          BIGINT,
    snapshot_date   DATE NOT NULL,
    session         VARCHAR(20) DEFAULT 'close',
    source          VARCHAR(50) DEFAULT 'api',
    created_at      TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(instrument_id, snapshot_date, session)
);

CREATE INDEX idx_market_instrument_date ON market_snapshots(instrument_id, snapshot_date DESC);

-- ============================================================
-- 5. SECTOR_PERFORMANCE — Hiệu suất ngành
-- ============================================================
CREATE TABLE IF NOT EXISTS sector_performance (
    id              SERIAL PRIMARY KEY,
    sector_name     VARCHAR(100) NOT NULL,
    etf_code        VARCHAR(20),
    change_pct      DECIMAL(8,4),
    volume          BIGINT,
    relative_strength DECIMAL(8,4),
    pe_forward      DECIMAL(8,2),
    foreign_net_billion_jpy DECIMAL(15,4),
    market_segment  VARCHAR(20),
    snapshot_date   DATE NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(sector_name, snapshot_date)
);

CREATE INDEX idx_sector_date ON sector_performance(snapshot_date DESC);
CREATE INDEX idx_sector_rs ON sector_performance(relative_strength DESC);

-- ============================================================
-- 6. ECONOMIC_INDICATORS — Chỉ số vĩ mô
-- ============================================================
CREATE TABLE IF NOT EXISTS economic_indicators (
    id              SERIAL PRIMARY KEY,
    indicator_name  VARCHAR(100) NOT NULL,
    value           DECIMAL(15,4) NOT NULL,
    unit            VARCHAR(20) DEFAULT '%',
    period          VARCHAR(30),
    country         VARCHAR(10) DEFAULT 'JP',
    source          VARCHAR(100),
    is_baseline     BOOLEAN DEFAULT FALSE,
    notes           TEXT DEFAULT '',
    recorded_at     TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(indicator_name, period)
);

CREATE INDEX idx_indicator_name ON economic_indicators(indicator_name, recorded_at DESC);
CREATE INDEX idx_indicator_baseline ON economic_indicators(is_baseline) WHERE is_baseline = TRUE;

-- ============================================================
-- 7. MARKET_CALENDAR — Lịch sự kiện thị trường
-- ============================================================
CREATE TABLE IF NOT EXISTS market_calendar (
    id              SERIAL PRIMARY KEY,
    event_date      DATE NOT NULL,
    event_time      TIME,
    event_type      VARCHAR(50) NOT NULL,
    title           VARCHAR(200) NOT NULL,
    description     TEXT DEFAULT '',
    country         VARCHAR(10) DEFAULT 'JP',
    impact_level    VARCHAR(10) DEFAULT 'MEDIUM'
                    CHECK (impact_level IN ('LOW', 'MEDIUM', 'HIGH')),
    actual_value    VARCHAR(50),
    forecast_value  VARCHAR(50),
    previous_value  VARCHAR(50),
    is_completed    BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_calendar_date ON market_calendar(event_date);
CREATE INDEX idx_calendar_type ON market_calendar(event_type, event_date);
CREATE INDEX idx_calendar_upcoming ON market_calendar(event_date)
    WHERE is_completed = FALSE;

-- ============================================================
-- 8. RECOMMENDATIONS — Khuyến nghị đầu tư
-- ============================================================
CREATE TABLE IF NOT EXISTS recommendations (
    id              SERIAL PRIMARY KEY,
    report_id       INTEGER REFERENCES reports(id) ON DELETE SET NULL,
    asset           VARCHAR(100) NOT NULL,
    action          VARCHAR(20) NOT NULL
                    CHECK (action IN ('BUY', 'WATCH', 'AVOID')),
    reasoning       TEXT NOT NULL,
    counter_argument TEXT DEFAULT '',
    framework       VARCHAR(50),
    price_at_recommendation DECIMAL(15,4),
    price_target    DECIMAL(15,4),
    outcome_pct     DECIMAL(8,4),
    outcome_notes   TEXT DEFAULT '',
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    expired_at      TIMESTAMPTZ
);

CREATE INDEX idx_recommendations_active ON recommendations(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_recommendations_asset ON recommendations(asset, created_at DESC);

-- ============================================================
-- 9. RISK_ALERTS — Cảnh báo rủi ro
-- ============================================================
CREATE TABLE IF NOT EXISTS risk_alerts (
    id              SERIAL PRIMARY KEY,
    risk_type       VARCHAR(50) NOT NULL,
    severity        VARCHAR(10) NOT NULL
                    CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    title           VARCHAR(200) NOT NULL,
    description     TEXT NOT NULL,
    trigger_data    JSONB DEFAULT '{}'::jsonb,
    action_taken    TEXT DEFAULT '',
    is_active       BOOLEAN DEFAULT TRUE,
    detected_at     TIMESTAMPTZ DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ
);

CREATE INDEX idx_risk_active ON risk_alerts(is_active, severity) WHERE is_active = TRUE;

-- ============================================================
-- 10. ANALYSIS_SNAPSHOTS — Kết luận phân tích
-- ============================================================
CREATE TABLE IF NOT EXISTS analysis_snapshots (
    id              SERIAL PRIMARY KEY,
    snapshot_date   DATE NOT NULL,
    economic_phase  VARCHAR(50),
    leading_sectors JSONB DEFAULT '[]'::jsonb,
    carry_trade_risk VARCHAR(20) DEFAULT 'LOW',
    yen_assessment  VARCHAR(30),
    market_outlook  VARCHAR(30),
    key_thesis      TEXT,
    confidence      INTEGER CHECK (confidence BETWEEN 1 AND 10),
    created_at      TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(snapshot_date)
);

CREATE INDEX idx_analysis_date ON analysis_snapshots(snapshot_date DESC);

-- ============================================================
-- SEED DATA — Instruments cơ bản
-- ============================================================
INSERT INTO instruments (symbol, name, asset_type, exchange, currency) VALUES
    ('NIKKEI225', 'Nikkei 225 Index',       'INDEX',     'TSE',    'JPY'),
    ('TOPIX',     'TOPIX Index',            'INDEX',     'TSE',    'JPY'),
    ('USDJPY',    'USD/JPY',                'FOREX',     'FOREX',  'JPY'),
    ('XAUUSD',    'Gold Spot',              'COMMODITY', 'COMEX',  'USD'),
    ('SP500',     'S&P 500 Index',          'INDEX',     'NYSE',   'USD'),
    ('NASDAQ',    'Nasdaq Composite',       'INDEX',     'NASDAQ', 'USD'),
    ('DXY',       'US Dollar Index',        'INDEX',     'ICE',    'USD'),
    ('VIX',       'CBOE Volatility Index',  'INDEX',     'CBOE',   'USD'),
    ('NK225F',    'Nikkei 225 Futures',     'FUTURES',   'CME',    'JPY')
ON CONFLICT (symbol) DO NOTHING;

-- Sector ETFs
INSERT INTO instruments (symbol, name, asset_type, exchange, currency, sector) VALUES
    ('1615.T', 'TOPIX Banks ETF',          'ETF', 'TSE', 'JPY', 'Banking'),
    ('1617.T', 'TOPIX Foods ETF',          'ETF', 'TSE', 'JPY', 'Foods'),
    ('1618.T', 'TOPIX Energy ETF',         'ETF', 'TSE', 'JPY', 'Energy'),
    ('1619.T', 'TOPIX Chemicals ETF',      'ETF', 'TSE', 'JPY', 'Chemicals'),
    ('1620.T', 'TOPIX Steel ETF',          'ETF', 'TSE', 'JPY', 'Steel'),
    ('1621.T', 'TOPIX Machinery ETF',      'ETF', 'TSE', 'JPY', 'Machinery'),
    ('1623.T', 'TOPIX Electronics ETF',    'ETF', 'TSE', 'JPY', 'Electronics'),
    ('1624.T', 'TOPIX Transport ETF',      'ETF', 'TSE', 'JPY', 'Transport'),
    ('1625.T', 'TOPIX Trading ETF',        'ETF', 'TSE', 'JPY', 'Trading'),
    ('1626.T', 'TOPIX Construction ETF',   'ETF', 'TSE', 'JPY', 'Construction')
ON CONFLICT (symbol) DO NOTHING;

-- Baseline economic indicators (§9)
INSERT INTO economic_indicators (indicator_name, value, unit, period, country, is_baseline, notes) VALUES
    ('BOJ_POLICY_RATE',  0.75, '%',     '2025-Q4', 'JP', TRUE, 'Tăng từ 0.5% tháng 12/2025'),
    ('JAPAN_CPI',        2.75, '%',     '2025-Q4', 'JP', TRUE, 'Trên mục tiêu 2% từ 2023'),
    ('SHUNTO_WAGE',      5.28, '%',     'FY2025',  'JP', TRUE, 'Lớn nhất 30 năm'),
    ('JAPAN_DEBT_GDP',   230,  '%',     '2025',    'JP', TRUE, 'Rủi ro nợ công'),
    ('FED_FUNDS_RATE',   4.50, '%',     '2025-Q4', 'US', TRUE, 'Federal Reserve target rate')
ON CONFLICT (indicator_name, period) DO NOTHING;
