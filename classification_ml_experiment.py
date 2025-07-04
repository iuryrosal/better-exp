import pandas as pd
import numpy as np
import pickle

from sklearn.model_selection import train_test_split

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC

from better_experimentation import BetterExperimentation

def process_data(dataframe):
	df = dataframe.sample(frac=1)

	# amount of fraud classes 492 rows.
	fraud_df = df.loc[df['Class'] == 1]
	non_fraud_df = df.loc[df['Class'] == 0][:492]

	normal_distributed_df = pd.concat([fraud_df, non_fraud_df])

	# Shuffle dataframe rows
	new_df = normal_distributed_df.sample(frac=1, random_state=42)

	return new_df


if __name__ == "__main__":
	np.random.seed(40)

	# https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud
	csv_path = "data/creditcard/creditcard.csv"

	try:
		data = pd.read_csv(csv_path, sep=",")
	except Exception as e:
		print(
			"Unable to download training & test CSV, check your internet connecion. Error: %s", e
		)
	non_fraud_df_to_test = data.loc[data['Class'] == 0][492:]
	non_fraud_df_to_test = non_fraud_df_to_test.drop(["Class"], axis=1)
	data = process_data(data)
	
	X = data.drop(["Class"], axis=1)
	Y = data[["Class"]]
	X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, train_size=0.7)

	X_test = pd.concat([non_fraud_df_to_test, X_test])
	df_non_fraud_values_to_test = {'Class': [0 for _ in range(len(non_fraud_df_to_test.values))]}
	y_test = pd.concat([pd.DataFrame(data=df_non_fraud_values_to_test), y_test])

	models = []
	models.append(LogisticRegression(solver="newton-cg"))
	models.append(KNeighborsClassifier())
	models.append(DecisionTreeClassifier())
	models.append(GaussianNB())
	models.append(SVC())
	models_trained = []
	for model in models:
		model.fit(X_train, y_train)
		models_trained.append(model)

	# using console
	for i, model in enumerate(models):
		with open(f'tests/local/classification/model_{i}.pkl','wb') as f:
			pickle.dump(model, f)
	
	X_test.to_csv("tests/local/classification/x_test.csv", index=False)
	y_test.to_csv("tests/local/classification/y_test.csv", index=False)

	# CLI: better_experimentation tests/local/classification tests/local/classification/x_test.csv tests/local/classification/y_test.csv accuracy

	# using library with files paths (similar with console)
	better_exp = BetterExperimentation(
		models_trained="tests/local/classification",
		X_test="tests/local/classification/x_test.csv",
		y_test="tests/local/classification/y_test.csv",
		scores_target="accuracy",
		report_name="library_with_path"
	)
	better_exp.run()

	# using library with current objects
	better_exp = BetterExperimentation(
		models_trained=models_trained,
		X_test=X_test,
		y_test=y_test,
		scores_target=["accuracy"],
		report_name="library_with_objects"
	)
	better_exp.run()

	# using both
	models_trained.append("tests/local/classification")
	better_exp = BetterExperimentation(
		models_trained=models_trained,
		X_test=X_test,
		y_test=y_test,
		scores_target=["accuracy"],
		report_name="library_with_both"
	)
	better_exp.run()