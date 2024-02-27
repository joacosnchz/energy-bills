# Introduction
This project obtains data form Emporia Energy API (unofficial) to generate invoices using Stripe

# Links
- [Emporia Energy API](https://emporia-connect.xyt.co.za/api/documentation#/)
- [Google sheets API](https://developers.google.com/sheets/api/quickstart/python)
- [Stripe API](https://docs.stripe.com/api)

# Setup local environment
1. Create `.env` file based on `.env.example` on `deployments/local` and on `migrations/`
2. Start local services: `cd deployments/local && docker compose up -d`
3. Run migrations: `cd migrations && ./upgrade.sh`

# Run
- To build: `deployments/local/build.sh`
- To run: `deployments/local/run.sh`
