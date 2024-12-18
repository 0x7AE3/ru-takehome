## Usage
```bash
# First, install the required packages
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Now run
```bash
python blackstone.py
```
to create `blackstone.db`, and likewise run
```bash
python janestreet.py
``` 
to create `janestreet.db`.
Next, run
```bash
python clean_blackstone.py && python clean_janestreet.py
```
to clean each database.
Finally, run
```bash
python evaluate.py
```
to <<<TODO>>>
