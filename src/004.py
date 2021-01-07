import pandas as pd
from pandas.core.algorithms import mode
import sklearn
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from sklearn import linear_model
import sklearn.model_selection

# 031 load data

use_log = pd.read_csv("../sample_codes/4章/use_log.csv")
use_log.isnull().sum()

customer = pd.read_csv("../sample_codes/4章/customer_join.csv")
customer.isnull().sum()

# 032 group customers with clustering

customer_clustering = customer[["mean", "median", "max", "min", "membership_period"]]
customer_clustering

sc = StandardScaler()
customer_clustering_sc = sc.fit_transform(customer_clustering)

kmeans = KMeans(n_clusters=4, random_state=0)
clusters = kmeans.fit(customer_clustering_sc)
customer_clustering["cluster"] = clusters.labels_
print(customer_clustering["cluster"].unique())
customer_clustering

# 033 analyze clustering result

customer_clustering.columns = ["月内平均値", "月内中央値", "月内最大値", "月内最小値", "会員期間", "cluster"]
customer_clustering.groupby("cluster").count()
customer_clustering.groupby("cluster").mean()

# 034 visualize analysis result

X = customer_clustering_sc
pca = PCA(n_components=2)
pca.fit(X)
x_pca = pca.transform(X)
pca_df = pd.DataFrame(x_pca)
pca_df["cluster"] = customer_clustering["cluster"]

for target_cluster in customer_clustering["cluster"].unique():
    tmp = pca_df.loc[pca_df["cluster"] == target_cluster]
    plt.scatter(tmp[0], tmp[1])


# 035 understand deleted customer tendency based on clustering result

customer_clustering = pd.concat([customer_clustering, customer], axis=1)
customer_clustering.groupby(["cluster", "is_deleted"], as_index=False).count()[
    ["cluster", "is_deleted", "customer_id"]
]

customer_clustering.groupby(["cluster", "routine_flg"], as_index=False).count()[
    ["cluster", "routine_flg", "customer_id"]
]

# 036 prepare to estimate next month use

use_log["usedate"] = pd.to_datetime(use_log["usedate"])
use_log["年月"] = use_log["usedate"].dt.strftime("%Y%m")
use_log_months = use_log.groupby(["年月", "customer_id"], as_index=False).count()
use_log_months.rename(columns={"log_id": "count"}, inplace=True)
del use_log_months["usedate"]

year_months = list(use_log_months["年月"].unique())
predict_data = pd.DataFrame()
for i in range(6, len(year_months)):
    tmp = use_log_months.loc[use_log_months["年月"] == year_months[i]]
    tmp.rename(columns={"count": "count_pred"}, inplace=True)
    for j in range(1, 7):
        tmp_before = use_log_months.loc[use_log_months["年月"] == year_months[i - j]]
        del tmp_before["年月"]
        tmp_before.rename(columns={"count": "count_{}".format(j - 1)}, inplace=True)
        tmp = pd.merge(tmp, tmp_before, on="customer_id", how="left")
    predict_data = pd.concat([predict_data, tmp], ignore_index=True)
predict_data

predict_data = predict_data.dropna()
predict_data = predict_data.reset_index(drop=True)
predict_data

# 037 add featured variables

predict_data = pd.merge(
    predict_data, customer[["customer_id", "start_date"]], on="customer_id", how="left"
)
predict_data["start_date"] = pd.to_datetime(predict_data["start_date"])
predict_data["now_date"] = pd.to_datetime(predict_data["年月"], format="%Y%m")
predict_data["period"] = None
for i in range(len(predict_data)):
    delta = relativedelta(predict_data["now_date"][i], predict_data["start_date"][i])
    predict_data["period"][i] = delta.years * 12 + delta.months


# 038 generate model
predict_data = predict_data.loc[
    predict_data["start_date"] >= pd.to_datetime("2018-04-01")
]
model = linear_model.LinearRegression()
X = predict_data[
    ["count_0", "count_1", "count_2", "count_3", "count_4", "count_5", "period"]
]
y = predict_data["count_pred"]
X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(X, y)
model.fit(X_train, y_train)

print(model.score(X_train, y_train))
print(model.score(X_test, y_test))

# 039 check variable

coef = pd.DataFrame({"feature_names": X.columns, "coefficient": model.coef_})
coef

# 40 predict next month usage

x1 = [3, 4, 4, 6, 8, 7, 8]
x2 = [2, 2, 3, 3, 4, 6, 8]

x_pred = [x1, x2]
model.predict(x_pred)

use_log_months.to_csv("use_log_months.dump.csv", index=False)