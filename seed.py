from config import connect, pick_shard


def create_library():
    conn = connect("library")
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS books")
    c.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, title TEXT, author TEXT, year INTEGER)")

    books = [
        ("1984", "George Orwell", 1949),
        ("The Hobbit", "J.R.R. Tolkien", 1937),
        ("To Kill a Mockingbird", "Harper Lee", 1960),
        ("The Great Gatsby", "F. Scott Fitzgerald", 1925),
        ("Harry Potter and the Philosopher's Stone", "J.K. Rowling", 1997),
    ]
    c.executemany("INSERT INTO books (title, author, year) VALUES (%s, %s, %s)", books)
    conn.commit()
    conn.close()


def create_school():
    conn = connect("school")
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS students")
    c.execute("CREATE TABLE students (id SERIAL PRIMARY KEY, name TEXT, age INTEGER, grade TEXT)")

    students = [
        ("Emma Virtanen", 17, "A"),
        ("Liam Korhonen", 18, "B"),
        ("Olivia Nieminen", 17, "A"),
        ("Noah Mäkinen", 16, "C"),
        ("Aino Laine", 18, "B"),
    ]
    c.executemany("INSERT INTO students (name, age, grade) VALUES (%s, %s, %s)", students)
    conn.commit()
    conn.close()


def create_store():
    products = [
        ("Laptop", 899.99, 12),
        ("Headphones", 59.90, 40),
        ("Keyboard", 34.50, 25),
        ("Mouse", 19.99, 60),
        ("Charger", 24.90, 35),
        ("Printer", 149.00, 5),
        ("Speaker", 79.90, 18),
        ("Tablet", 329.00, 10),
        ("USB Cable", 9.99, 100),
        ("Webcam", 45.00, 15),
    ]

    for shard in [0, 1]:
        conn = connect("store", shard)
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS products")
        c.execute("CREATE TABLE products (id SERIAL PRIMARY KEY, name TEXT, price NUMERIC(10, 2), stock INTEGER)")

        for p in products:
            if pick_shard("store", p[0]) == shard:
                c.execute("INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)", p)
        conn.commit()
        conn.close()


def create_all():
    create_library()
    create_school()
    create_store()


if __name__ == "__main__":
    create_all()
