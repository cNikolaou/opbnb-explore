# opBNB Explore

A system for retrieving, indexing and presenting data from [opBNB](https://docs.bnbchain.org/opbnb-docs/docs/intro/).
The appliacation can be run locally so users do not need to depend or trust
third-parties to access and opBNB data in a useful format. This can be fully
achieved when you run your own opBNB node locally and you use the RPC
endpoint from that node for accessing the blockchain data.

The pipeline consists of 3 components:
- An ETL pipeline that fetches data from an opBNB RPC endpoint. This can be
a node running locally or an endpoint from a provider
- A PostgreSQL database to store and index the data from the ETL pipeline
- A Next.js application that connects to the database and presents
information to the users


![Alt Text](docs/system.svg)


There are some other optional modules that are not part of the main system,
such as the `uploader.py` which can be used for uploading the intermediate
CSV files to an S3-compatible object storage.

## Running

There are two ways to run the whole system. You can run with Docker
Compose or run a Python and a Node processes.

In either case you want to probably configure the `PROVIDER_URI`.

The default provider used is the `https://opbnb-mainnet-rpc.bnbchain.org`. You
can find more information on the [opBNB Documentation](https://docs.bnbchain.org/opbnb-docs/docs/build-on-opbnb/opbnb-network-info/#opbnb-rpc-endpoints). However this provider has limits (which are currently enough for
fetching new data but it will take too long to fetch historical data).

In either case it's better to configure the system by using an `.env` file. To
create a copy of the example run:

```bash
cp .env.example .env
```

Then you can customise the options and add new ones. The `etl/settings.py`
has a list of all the environment variables that you can configure.


### Run with Docker Compose

To run with Docker Compose:

```bash
docker compose up -d
```

You can configure the `./compose.yaml` file if you want to make any
changes, but that is not required. It is better to make any configuration
changes to the `.env` file as this is loaded to the `etl` in the `compose.yaml`
file.

Make sure that the `POSTGRES_DB` name is unique and you do not have another
Postgres database on your local machine with the same name as we found that that
was creating an issue.

### Run Directly on Host Machine

To run on the host machine directly you need to:

1. Run a PostgreSQL database and create a new database. Update the `.env` file
with the name you of the database to the `DB_NAME` variable.

2. Create a Python virtual environment and run the Python process that will
fetch the data and load them to the database.
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r etl/requirements.txt
python etl/main.py
```

3. Start the Next.js application
```bash
cd viewer
npm install
npm run dev
```

4. Then go to http://localhost:3000