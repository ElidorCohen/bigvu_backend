from app.db import SingletonDB, init_db


def test_singleton_db(client):
    db1 = SingletonDB(client)
    db2 = SingletonDB(client)

    assert db1 is db2
    assert db1.client is db2.client
    assert db1.db is db2.db

    init_db(client)
    assert client.mongo is db1
    assert client.mongo is db2
