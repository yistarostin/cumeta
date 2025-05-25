import clickhouse_connect

client = clickhouse_connect.get_client(user="cumeta", password="veuve_clicquot")

print(list(client.query("SELECT * from system.contributors").result_rows))
