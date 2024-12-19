## Setup
First, install the required packages:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Now run
```bash
python blackstone.py && python janestreet.py
```
to create `blackstone.db` and `janestreet.db`. 
Each script will only construct a database if it doesn't already exist.
Use the `-f` flag in either command to force overwrite an existing database.
## Usage
Once you have created the databases per the instructions above, you can search them with natural language. 
For example:
```bash
python search_janestreet.py "trading nyc new grad"
```
or
```bash
python search_blackstone.py "private equity london"
```
Each script will compute embeddings if they don't already exist in the database. 
Use the `-f` flag in either command to force recompute the embeddings.
## Design Choices
- SQLite was chosen as the database engine because it is lightweight and easy to use. 
  For example, you can view the contents of the databases by running
  ```bash
  datasette serve blackstone.db janestreet.db
  ```
  and visiting http://localhost:8001
- The `search_janestreet.py` and `search_blackstone.py` scripts are separate because the schema of the two databases is different. Ideally there would be another pre-processing step to unify the schemas, especially if you are scraping more than two websites.
- The natural language querying of each database is thanks to [SentenceTransformers](SentenceTransformers). Using [OpenAI Embeddings](https://platform.openai.com/docs/api-reference/embeddings) would most likely yield more accurate results, but the present way has the advantage of being self-hosted (no external API calls --> no fees).
