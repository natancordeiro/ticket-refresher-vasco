import argparse
from ticket_refresher.config import load_config
from ticket_refresher.logging_config import logger
from ticket_refresher.app import App

def parse_args():
    ap = argparse.ArgumentParser(
        description="Renovador de expiração do carrinho (Eleven Tickets - Vasco) via DrissionPage."
    )
    ap.add_argument("--once", action="store_true", help="Executa somente um ciclo (para teste).")
    return ap.parse_args()

def main():
    args = parse_args()
    cfg = load_config()
    logger.info("Config carregada. Iniciando aplicação.")

    app = App(cfg)
    if args.once:
        app.run_once()
    else:
        app.run_forever()

if __name__ == "__main__":
    main()
