from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


TradingMode = Literal["simulator", "paper", "live"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "NexusQuant API"
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    trading_mode: TradingMode = Field(default="simulator", alias="TRADING_MODE")
    scanner_interval_seconds: int = Field(default=1, alias="SCANNER_INTERVAL_SECONDS")
    ai_threshold: float = Field(default=70.0, alias="AI_THRESHOLD")
    stale_feed_seconds: int = Field(default=4, alias="STALE_FEED_SECONDS")

    # Upstox
    upstox_api_key: str = Field(default="", alias="UPSTOX_API_KEY")
    upstox_access_token: str = Field(default="", alias="UPSTOX_ACCESS_TOKEN")
    upstox_base_url: str = Field(default="https://api.upstox.com/v2", alias="UPSTOX_BASE_URL")
    upstox_market_authorize_endpoint: str = Field(
        default="/v3/feed/market-data-feed/authorize", alias="UPSTOX_MARKET_AUTHORIZE_ENDPOINT"
    )
    upstox_profile_endpoint: str = Field(default="/user/profile", alias="UPSTOX_PROFILE_ENDPOINT")

    nifty_instrument_key: str = Field(default="NSE_INDEX|Nifty 50", alias="NIFTY_INSTRUMENT_KEY")
    sensex_instrument_key: str = Field(default="BSE_INDEX|SENSEX", alias="SENSEX_INSTRUMENT_KEY")

    # Storage
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/nexusquant",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # Risk
    daily_capital: float = Field(default=300000.0, alias="DAILY_CAPITAL")
    capital_allocation_pct: float = Field(default=10.0, alias="CAPITAL_ALLOCATION_PCT")
    max_exposure_pct: float = Field(default=40.0, alias="MAX_EXPOSURE_PCT")
    max_daily_drawdown_pct: float = Field(default=5.0, alias="MAX_DAILY_DRAWDOWN_PCT")
    max_slippage_bps: float = Field(default=20.0, alias="MAX_SLIPPAGE_BPS")
    max_latency_ms: int = Field(default=250, alias="MAX_LATENCY_MS")
    cooldown_after_losses: int = Field(default=3, alias="COOLDOWN_AFTER_LOSSES")
    require_live_upstox_connection: bool = Field(default=True, alias="REQUIRE_LIVE_UPSTOX_CONNECTION")

    # ML / Data collection
    ai_model_path: str = Field(default="./artifacts/ai/scalp_model.joblib", alias="AI_MODEL_PATH")
    ai_training_min_samples: int = Field(default=1200, alias="AI_TRAINING_MIN_SAMPLES")
    ai_training_rows: int = Field(default=60000, alias="AI_TRAINING_ROWS")
    ai_label_lookahead_seconds: int = Field(default=18, alias="AI_LABEL_LOOKAHEAD_SECONDS")
    ai_target_points: float = Field(default=5.0, alias="AI_TARGET_POINTS")
    ai_probability_weight: float = Field(default=0.35, alias="AI_PROBABILITY_WEIGHT")
    ai_min_probability: float = Field(default=0.58, alias="AI_MIN_PROBABILITY")
    ai_auto_train_enabled: bool = Field(default=True, alias="AI_AUTO_TRAIN_ENABLED")
    ai_auto_retrain_seconds: int = Field(default=900, alias="AI_AUTO_RETRAIN_SECONDS")

    # Monitoring
    prometheus_enabled: bool = Field(default=True, alias="PROMETHEUS_ENABLED")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
