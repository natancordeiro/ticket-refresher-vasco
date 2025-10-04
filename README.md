# Ticket Refresher (DrissionPage)

Automação para manter o carrinho ativo no site de ingressos do Vasco (Eleven Tickets), refazendo o fluxo de checkout e gerando o QR de pagamento em intervalos regulares.
Foco em produção: logs detalhados, retry+backoff, screenshots em erro, config centralizada, OOP e modular.

## Requisitos
- Python 3.10+
- Google Chrome / Chromium compatível com DrissionPage
- Pacotes: `pip install -r requirements.txt`

## Estrutura de pastas
```
ticket-refresher/
├─ main.py
├─ README.md
├─ requirements.txt
├─ .env.example
├─ config.yaml            # opcional (sobrepõe .env parcialmente)
└─ ticket_refresher/
   ├─ __init__.py
   ├─ version.py
   ├─ logging_config.py
   ├─ exceptions.py
   ├─ config.py
   ├─ timing.py
   ├─ retry.py
   ├─ utils.py
   ├─ browser.py
   ├─ app.py
   ├─ parsers/
   │  ├─ __init__.py
   │  ├─ auth_parsers.py
   │  └─ cart_parsers.py
   ├─ services/
   │  ├─ __init__.py
   │  ├─ auth.py
   │  ├─ cart.py
   │  └─ payment.py
   └─ persistence/
      ├─ __init__.py
      ├─ sink.py
      └─ json_sink.py
```

## Configuração
1. Copie `.env.example` para `.env` e preencha:
   - `LOGIN_EMAIL`, `LOGIN_PASSWORD`
   - Ajuste `HEADLESS`, intervalos e timeouts conforme desejar
2. (Opcional) Sobreponha parâmetros em `config.yaml`.
3. Certifique-se de que a pasta de perfil e de screenshots existem ou serão criadas:
   - `USER_DATA_DIR=.dp_profile`
   - `SCREENSHOT_DIR=screenshots`

### `.env.example`
```bash
# Modo de execução
APP_ENV=production
HEADLESS=false
USER_DATA_DIR=.dp_profile        # perfil do Chromium isolado
SCREENSHOT_DIR=screenshots
LOG_LEVEL=DEBUG

# Alvo e rotinas
BASE_URL=https://vasco.eleventickets.com/?lang=pt_BR#!/home
CART_URL=https://vasco.eleventickets.com/#!/carrinho

# Credenciais
LOGIN_EMAIL=usuario@example.com
LOGIN_PASSWORD=troque_me

# Intervalos e timeouts (segundos)
WAIT_QR_SLEEP=10
RENEW_WAIT_MINUTES=20
NAVIGATION_TIMEOUT=30
ELEMENT_TIMEOUT=20
RETRY_MAX_ATTEMPTS=3
RETRY_BACKOFF_BASE=2
RETRY_BACKOFF_JITTER=true
```

### `config.yaml` (opcional)
```yaml
headless: false
renew_wait_minutes: 20
wait_qr_sleep: 10
navigation_timeout: 30
element_timeout: 20
retry:
  max_attempts: 3
  backoff_base: 2
  jitter: true
```

## Instalação
```bash
pip install -r requirements.txt
```

## Execução
```bash
python main.py         # loop infinito (produção)
python main.py --once  # executa um ciclo (teste)
```

## Fluxo da Automação
1. Abre a HOME.
2. Se não estiver logado, realiza login:
   - Clica **Login** → **Público Geral - Jogos** → preenche credenciais → **Login**.
   - Aceita redirecionamento para **FacialRecognition** ou **Home**; valida `<a ng-show="User">`.
3. Vai ao carrinho.
4. Clica **CONTINUAR PARA CHECKOUT SEGURO** → **Seguir para o pagamento**.
5. Aguarda `<img.imply-pay-qrcode>`; salva o QR (base64→PNG) e um JSON de sessão.
6. Espera `WAIT_QR_SLEEP` segundos.
7. Volta ao carrinho.
8. Aguarda `RENEW_WAIT_MINUTES` minutos.
9. Repete.

## Observabilidade
- **Logs**: console colorido + arquivo `logs/app.log` (usa exatamente seu template).
- **Request iniciado/finalizado**: cada `goto(url)` registra tempo e bytes aproximados (`len(html)`).
- **Retry + backoff**: operações críticas usam backoff exponencial com jitter (configurável).
- **Parsing**: ao capturar QR, loga `itens_extraídos=1` e `página=checkout`.
- **Persistência**: QR salvo em PNG e metadados em JSON (`runs/session_*.json`).
- **Erros**: `TipoErro + mensagem`; screenshots automáticas em `screenshots/`.

## Extensibilidade
- **Parsers** (`ticket_refresher/parsers/*`): centralizam seletores e transformações por página.
- **Sinks** (`ticket_refresher/persistence/*`): para trocar JSON por DB/S3, implemente `Sink.persist`.
- **Serviços** (`ticket_refresher/services/*`): encapsulam fluxos (auth, carrinho, pagamento).

## Dicas
- Se o site alterar marcadores/atributos, ajuste seletores em `services/*.py`.
- Em caso de falha de login/checkout, consulte `logs/app.log` e as screenshots de erro.
- Para rodar headless em servidor, defina `HEADLESS=true` e garanta dependências do Chromium.
