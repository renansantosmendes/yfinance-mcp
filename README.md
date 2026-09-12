# yfinance-mcp

Servidor **MCP (Model Context Protocol)** que expõe os dados do Yahoo Finance
através da biblioteca [`yfinance`](https://github.com/ranaroussi/yfinance),
construído com **FastAPI + FastMCP** e pronto para deploy na **Vercel**.

## Arquitetura

```
yfinance-mcp/
├── api/
│   └── index.py           # entrypoint serverless da Vercel (importa app.main:app)
├── app/
│   ├── main.py             # FastAPI app; monta o servidor MCP em /mcp
│   ├── mcp_server.py        # instância FastMCP + registro das tools
│   ├── tools/
│   │   ├── company.py       # get_company_info, get_fast_info, get_isin
│   │   ├── price.py         # histórico, dividendos, splits, shares
│   │   ├── financials.py     # DRE, balanço, fluxo de caixa
│   │   ├── holders.py        # holders institucionais/insiders
│   │   ├── analysis.py       # recomendações, estimativas, calendário, news
│   │   ├── options.py        # opções (calls/puts)
│   │   └── market.py         # download multi-ticker, search, lookup, market status
│   └── utils/
│       ├── ticker_cache.py    # cache de yf.Ticker por símbolo
│       └── serialization.py   # conversão de DataFrame/Series/numpy -> JSON
├── requirements.txt
├── vercel.json
└── .python-version
```

O servidor MCP roda em modo **stateless HTTP** (`stateless_http=True`), ideal
para ambientes serverless como a Vercel, onde cada invocação pode cair em uma
instância diferente (sem estado de sessão compartilhado entre requisições).

## Tool principal

### `get_company_info(ticker: str)`

Retorna o **perfil completo** da empresa/ativo: nome, setor, indústria,
resumo do negócio, site, país, número de funcionários, métricas de
valuation (P/L, EV/EBITDA, PEG, P/VP), dados de preço (atual, máxima/mínima
52 semanas, volume), dividendos (yield, payout ratio, data ex-dividendo),
margens, preço-alvo dos analistas, e todos os demais campos do `Ticker.info`
do yfinance.

```python
get_company_info(ticker="AAPL")
get_company_info(ticker="PETR4.SA")   # ações da B3
```

## Demais tools (40 no total)

| Categoria | Tools |
|---|---|
| Empresa | `get_company_info`, `get_fast_info`, `get_isin` |
| Preço/histórico | `get_history`, `get_dividends`, `get_splits`, `get_capital_gains`, `get_actions`, `get_shares_outstanding` |
| Demonstrações financeiras | `get_income_statement`, `get_balance_sheet`, `get_cashflow` (todas com flag `quarterly`) |
| Ownership | `get_major_holders`, `get_institutional_holders`, `get_mutualfund_holders`, `get_insider_transactions`, `get_insider_purchases`, `get_insider_roster_holders` |
| Análise/Analistas | `get_recommendations`, `get_recommendations_summary`, `get_upgrades_downgrades`, `get_analyst_price_targets`, `get_earnings_estimate`, `get_revenue_estimate`, `get_earnings_history`, `get_eps_trend`, `get_eps_revisions`, `get_growth_estimates`, `get_calendar`, `get_earnings_dates`, `get_sustainability`, `get_sec_filings`, `get_news` |
| Opções | `get_options_expirations`, `get_option_chain` |
| Mercado (multi-ticker) | `download_history`, `search_symbols`, `lookup_symbols`, `get_market_status`, `get_multiple_quotes` |

Todas as tools têm docstrings detalhadas (visíveis para o cliente MCP) e
aceitam o parâmetro `ticker` no formato do Yahoo Finance (ex.: `AAPL`,
`PETR4.SA`, `^GSPC`, `BTC-USD`).

## Rodando localmente

```bash
py -3.12 -m venv .venv
source .venv/Scripts/activate   # Windows (git bash) — no PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt          # apenas dependências de runtime
# ou, para desenvolver (testes + lint):
pip install -r requirements-dev.txt

uvicorn app.main:app --reload --port 8000
```

- Healthcheck: `GET http://localhost:8000/health`
- Info do serviço: `GET http://localhost:8000/`
- Endpoint MCP (streamable-http): `http://localhost:8000/mcp`
- Docs REST auto-geradas (rotas não-MCP): `http://localhost:8000/docs`

Testando a tool principal com o cliente `fastmcp`:

```python
import asyncio
from fastmcp import Client

async def main():
    async with Client("http://localhost:8000/mcp") as client:
        result = await client.call_tool("get_company_info", {"ticker": "AAPL"})
        print(result.data)

asyncio.run(main())
```

## Testes e qualidade de código

O projeto tem **suíte de testes unitários (pytest)** cobrindo 100% do código em
`app/` e **lint (pylint)** configurado para o código de aplicação e para os
testes (com regras separadas — ver `.pylintrc` e `tests/.pylintrc`).

Nenhum teste bate na Yahoo Finance de verdade: cada teste substitui
`get_ticker` (ou a função/classe correspondente do módulo `yfinance`) por um
dublê (`tests/conftest.py::FakeTicker` e fakes locais), então a suíte roda
rápida, determinística e sem depender de rede ou de rate limit da Yahoo.

```bash
pip install -r requirements-dev.txt

# rodar todos os testes
pytest

# com relatório de cobertura
pytest --cov=app --cov-report=term-missing

# lint do código de aplicação (api/index.py, app/**)
pylint app api

# lint dos testes (regras um pouco mais permissivas: sem exigir
# docstring por teste, permite classes "fake" com poucos métodos)
pylint --rcfile=tests/.pylintrc tests
```

Estrutura dos testes:

| Arquivo | Cobre |
|---|---|
| `tests/test_serialization.py` | conversão DataFrame/Series/numpy → JSON, NaN/NaT, Timestamp |
| `tests/test_params.py` | helper `build_period_kwargs` (period vs. start/end) |
| `tests/test_ticker_cache.py` | cache de `yf.Ticker` (normalização, dedup, símbolo inválido) |
| `tests/test_main.py` | rotas não-MCP do FastAPI (`/`, `/health`, `/docs`) |
| `tests/test_tools_*.py` | cada tool individualmente, com yfinance mockado |
| `tests/test_mcp_integration.py` | round-trip real via protocolo MCP (transporte em memória) |

## CI (GitHub Actions)

O workflow em `.github/workflows/ci.yml` roda em todo push/PR para `main`:

1. `pylint app api` — lint do código de aplicação (deve ficar em 10.00/10).
2. `pylint --rcfile=tests/.pylintrc tests` — lint dos testes.
3. `pytest --cov=app --cov-fail-under=90` — testes com gate mínimo de 90% de
   cobertura (o projeto está em 100%).

## Deploy na Vercel

O projeto já inclui `vercel.json` apontando para `api/index.py` (que expõe o
`app` do FastAPI), usando o builder `@vercel/python`.

```bash
npm i -g vercel   # se ainda não tiver a CLI
vercel login
vercel             # deploy de preview
vercel --prod      # deploy de produção
```

Após o deploy, o endpoint MCP ficará em:

```
https://<seu-projeto>.vercel.app/mcp
```

### Observações importantes para produção

- **Timeout de função**: chamadas ao Yahoo Finance podem levar alguns
  segundos (principalmente `download_history` com vários tickers ou
  `get_option_chain`). No plano Hobby da Vercel o timeout padrão é curto
  (~10s); se necessário, aumente o `maxDuration` da função no painel do
  projeto ou faça upgrade de plano.
- **Rate limiting do Yahoo Finance**: o yfinance consulta endpoints não
  oficiais do Yahoo Finance; uso excessivo pode ser temporariamente
  limitado (HTTP 429). Não há chave de API necessária.
- **Cold start**: como é serverless, a primeira requisição após um período
  de inatividade pode ser mais lenta.

## Conectando em um cliente MCP (ex.: Claude Desktop / Claude Code)

Adicione um servidor MCP remoto (HTTP) apontando para a URL publicada:

```json
{
  "mcpServers": {
    "yfinance": {
      "url": "https://<seu-projeto>.vercel.app/mcp"
    }
  }
}
```

Ou, via Claude Code CLI:

```bash
claude mcp add --transport http yfinance https://<seu-projeto>.vercel.app/mcp
```

## Tratamento de erros

Erros do yfinance (ticker inválido, sem dados disponíveis, falha de rede)
propagam como erro de tool do MCP (`isError: true`) com a mensagem original,
permitindo que o cliente/LLM trate o caso adequadamente.
