# apgorm
[![pytest](https://github.com/TrigonDev/apgorm/actions/workflows/pytest.yml/badge.svg)](https://github.com/TrigonDev/apgorm/actions/workflows/pytest.yml)
[![pypi](https://github.com/TrigonDev/apgorm/actions/workflows/pypi.yml/badge.svg)](https://pypi.org/project/apgorm)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/TrigonDev/apgorm/main.svg)](https://results.pre-commit.ci/latest/github/TrigonDev/apgorm/main)
[![codecov](https://codecov.io/gh/TrigonDev/apgorm/branch/main/graph/badge.svg?token=LEY276K4NS)](https://codecov.io/gh/TrigonDev/apgorm)

[Documentation](https://github.com/trigondev/apgorm/wiki) | [CONTRIBUTING.md](https://github.com/trigondev/.github/tree/main/CONTRIBUTING.md)

An asynchronous ORM wrapped around asyncpg. Examples can be found under `examples/`. Run examples with `python -m examples.<example_name>` (`python -m examples.basic`).

Please note that this library is not for those learning SQL or Postgres. Although the basic usage of apgorm is straightforward, you will run into problems, especially with migrations, if you don't understand regular SQL well.

## Features
 - Fairly straightforward and easy-to-use.
 - Support for basic migrations.
 - Protects against SQL-injection.
 - Python-side converters and validators.
 - Decent many-to-many support.
 - Fully type-checked.
 - Tested.

## Limitations
 - Limited column namespace. For example, you cannot have a column named `tablename` since that is used to store the name of the model.
 - Only supports PostgreSQL with asyncpg.
 - Migrations don't natively support field/table renaming, but you can still write your own migration with raw SQL.

## Basic Usage
Defining a model and database:
```py
class User(apgorm.Model):
    username = VarChar(32).field()
    email = VarChar().nullablefield()
    
    primary_key = (username,)
    
class Database(apgorm.Database):
    users = User
```

Intializing the database:
```py
db = Database(migrations_folder=pathlib.Path("path/to/migrations"))
await db.connect(database="database name")
```

Creating & Applying migrations:
```py
if db.must_create_migrations():
    db.create_migrations()
if await db.must_apply_migrations():
    await db.apply_migrations()
```

Basic create, fetch, update, and delete:
```py
user = await User(username="Circuit").create()
print("Created user", user)

assert user == await User.fetch(username="Circuit")

user.email.v = "email@example.com"
await user.save()

await user.delete()
```
