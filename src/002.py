import pandas as pd

# 011 load the data
uriage_data = pd.read_csv("../sample_codes/2章/uriage.csv")
uriage_data.head()

kokyaku_data = pd.read_excel("../sample_codes/2章/kokyaku_daicho.xlsx")
kokyaku_data.head()

# 012 check wrong records of the data
uriage_data["item_name"].head()
uriage_data["item_price"].head()

# 013 analyze with wrong records
uriage_data["purchase_date"] = pd.to_datetime(uriage_data["purchase_date"])
uriage_data["purchase_month"] = uriage_data["purchase_date"].dt.strftime("%Y%m")
res = uriage_data.pivot_table(
    index="purchase_month",
    columns="item_name",
    aggfunc="size",
    fill_value=0,
)
res

res = uriage_data.pivot_table(
    index="purchase_month",
    columns="item_name",
    values="item_price",
    aggfunc="sum",
    fill_value=0,
)
res

# 014 modify item name
print(len(pd.unique(uriage_data["item_name"])))

uriage_data["item_name"] = uriage_data["item_name"].str.upper()
uriage_data["item_name"] = uriage_data["item_name"].str.replace("　", "")
uriage_data["item_name"] = uriage_data["item_name"].str.replace(" ", "")
uriage_data.sort_values(by=["item_name"], ascending=True)

print(pd.unique(uriage_data["item_name"]))
print(len(pd.unique(uriage_data["item_name"])))

# 015 complement NaN of item price

uriage_data.isnull().any(axis=0)

flg_is_null = uriage_data["item_price"].isnull()
list(uriage_data.loc[flg_is_null, "item_name"].unique())


for trg in list(uriage_data.loc[flg_is_null, "item_name"].unique()):
    flg_is_num = ~flg_is_null
    price = uriage_data.loc[
        (flg_is_num) & (uriage_data["item_name"] == trg), "item_price"
    ].max()
    uriage_data["item_price"].loc[
        (flg_is_null) & (uriage_data["item_name"] == trg)
    ] = price
uriage_data.head()

uriage_data.isnull().any(axis=0)

for trg in list(uriage_data["item_name"].sort_values().unique()):
    print(
        "["
        + trg
        + "] max: "
        + str(uriage_data.loc[uriage_data["item_name"] == trg, "item_price"].max())
        + " min: "
        + str(
            uriage_data.loc[uriage_data["item_name"] == trg, "item_price"].min(
                skipna=False,
            )
        )
    )

# 016 modify kokyaku name

kokyaku_data["顧客名"].head()
uriage_data["customer_name"].head()

kokyaku_data["顧客名"] = kokyaku_data["顧客名"].str.replace(" ", "")
kokyaku_data["顧客名"] = kokyaku_data["顧客名"].str.replace("　", "")

kokyaku_data["顧客名"].head()

# 017 modify date

flg_is_serial = kokyaku_data["登録日"].astype("str").str.isdigit()
flg_is_serial.sum()
from_serial = pd.to_timedelta(
    kokyaku_data.loc[flg_is_serial, "登録日"].astype("float"), unit="D"
) + pd.to_datetime("1900/01/01")
from_serial

from_string = pd.to_datetime(kokyaku_data.loc[~flg_is_serial, "登録日"])
from_string

kokyaku_data["登録日"] = pd.concat([from_string, from_serial])
kokyaku_data.head()

kokyaku_data["登録年月"] = kokyaku_data["登録日"].dt.strftime("%Y%m")
kokyaku_data.groupby("登録年月").count()["顧客名"].sum() == len(kokyaku_data)

flg_is_serial = kokyaku_data["登録日"].astype("str").str.isdigit()
flg_is_serial.sum()

# 018 join the two data lists

join_data = pd.merge(
    uriage_data,
    kokyaku_data,
    left_on="customer_name",
    right_on="顧客名",
    how="left",
)
join_data = join_data.drop("customer_name", axis=1)
join_data

# dump the cleansed data
dump_data = join_data[
    [
        "purchase_date",
        "purchase_month",
        "item_name",
        "item_price",
        "顧客名",
        "かな",
        "地域",
        "メールアドレス",
        "登録日",
        "登録年月",
    ]
]
dump_data

dump_data.to_csv("dump_data.dump.csv", index=False)

# analyze the data
imported_data = pd.read_csv("./dump_data.dump.csv")
imported_data

by_item = imported_data.pivot_table(
    index="purchase_month",
    columns="item_name",
    aggfunc="size",
    fill_value=0,
)
by_item

by_price = imported_data.pivot_table(
    index="purchase_month",
    columns="item_name",
    values="item_price",
    aggfunc="sum",
    fill_value=0,
)
by_price

by_customer = imported_data.pivot_table(
    index="purchase_month",
    columns="顧客名",
    aggfunc="size",
    fill_value=0,
)
by_customer

by_region = imported_data.pivot_table(
    index="purchase_month",
    columns="地域",
    aggfunc="size",
    fill_value=0,
)
by_region

away_data = pd.merge(
    uriage_data,
    kokyaku_data,
    left_on="customer_name",
    right_on="顧客名",
    how="right",
)
away_data
away_data[away_data["purchase_date"].isnull()][["顧客名", "メールアドレス", "登録日"]]
