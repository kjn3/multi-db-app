import psycopg2

DATABASES = {
    "library": {"label": "Library", "table": "books", "columns": ["title", "author", "year"], "ports": [5441]},
    "school": {"label": "School", "table": "students", "columns": ["name", "age", "grade"], "ports": [5442]},
    "store": {"label": "Store", "table": "products", "columns": ["name", "price", "stock"], "ports": [5443, 5444]},
}


def connect(db_name, shard=0):
    port = DATABASES[db_name]["ports"][shard]
    return psycopg2.connect(host="localhost", port=port, dbname=db_name, user="postgres", password="postgres")


def pick_shard(db_name, name):
    if len(DATABASES[db_name]["ports"]) == 1:
        return 0
    if name[0].upper() <= "M":
        return 0
    return 1
