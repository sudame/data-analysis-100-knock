import pandas as pd
import matplotlib.pyplot as plt

# 001 load data
customer_master = pd.read_csv("../../sample_codes/1章/customer_master.csv")
customer_master.head()

item_master = pd.read_csv("../../sample_codes/1章/item_master.csv")
item_master.head()

transaction_1 = pd.read_csv("../../sample_codes/1章/transaction_1.csv")
transaction_1.head()

transaction_detail_1 = pd.read_csv("../../sample_codes/1章/transaction_detail_1.csv")
transaction_detail_1.head()


# 002 union data
transaction_2 = pd.read_csv("../../sample_codes/1章/transaction_2.csv")
transaction = pd.concat(
    [transaction_1, transaction_2],
    ignore_index=True,
)
transaction.head()

print(len(transaction_1))
print(len(transaction_2))
print(len(transaction))

transaction_detail_2 = pd.read_csv("../../sample_codes/1章/transaction_detail_2.csv")
transaction_detail = pd.concat(
    [transaction_detail_1, transaction_detail_2],
    ignore_index=True,
)
transaction_detail.head()


# 003 join data
join_data = pd.merge(
    transaction_detail,
    transaction[["transaction_id", "payment_date", "customer_id"]],
    on="transaction_id",
    how="left",
)
join_data.head()

print(len(transaction_detail))
print(len(transaction))
print(len(join_data))

# 004 join master data
join_data = pd.merge(
    join_data,
    customer_master,
    on="customer_id",
    how="left",
)

join_data = pd.merge(
    join_data,
    item_master,
    on="item_id",
    how="left",
)

join_data.head()

# 005 add necessary data column
join_data["price"] = join_data["item_price"] * join_data["quantity"]
join_data.head()

# 006 check the data
print(join_data["price"].sum())
print(transaction["price"].sum())

join_data["price"].sum() == transaction["price"].sum()

# 007 check basic statistics of the data
join_data.isnull().sum()
join_data.describe()

join_data["payment_date"].min()
join_data["payment_date"].max()

# 008 slice the data into months

join_data.dtypes
join_data["payment_date"] = pd.to_datetime(join_data["payment_date"])
join_data["payment_month"] = join_data["payment_date"].dt.strftime("%Y%m")
join_data[["payment_date", "payment_month"]].head()

join_data.groupby("payment_month").sum()["price"]

# 009 use groupby for months and items

join_data.groupby(["payment_month", "item_name"]).sum()[["price", "quantity"]]
pd.pivot_table(
    join_data,
    index="item_name",
    columns="payment_month",
    values=["price", "quantity"],
    aggfunc="sum",
)

# 010 visualize sales trends

graph_data = pd.pivot_table(
    join_data,
    index="payment_month",
    columns="item_name",
    values="price",
    aggfunc="sum",
)
graph_data

plt.plot(list(graph_data.index), graph_data["PC-A"], label="PC-A")
plt.plot(list(graph_data.index), graph_data["PC-B"], label="PC-B")
plt.plot(list(graph_data.index), graph_data["PC-C"], label="PC-C")
plt.plot(list(graph_data.index), graph_data["PC-D"], label="PC-D")
plt.plot(list(graph_data.index), graph_data["PC-E"], label="PC-E")
plt.legend()
