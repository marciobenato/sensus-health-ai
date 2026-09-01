from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "01_DADOS"
RAW_DIR = DATA_DIR / "raw"
STAGING_DIR = DATA_DIR / "staging"
PROCESSED_DIR = DATA_DIR / "processed"
QUALITY_DIR = DATA_DIR / "quality"

UF = "SP"
YEAR = 2025
MONTHS = list(range(1, 13))
EXPECTED_COMPETENCIAS = [f"{YEAR}{month:02d}" for month in MONTHS]

SIH_SQLITE = STAGING_DIR / "sih_sp_2025.sqlite"
SIH_TABLE = "sih_rd_sp_2025"
CNES_SNAPSHOT_JSON = RAW_DIR / "cnes" / "hospitais_leitos_sp_2025_snapshot.json"
CNES_API_JSON = RAW_DIR / "cnes" / "cnes_estabelecimentos_sih_sp_2025_api.json"
REGIOES_CSV = RAW_DIR / "auxiliar" / "regioes_saude_sp.csv"
ETAPA2_REPORT = QUALITY_DIR / "relatorio_validacao_dados.json"
