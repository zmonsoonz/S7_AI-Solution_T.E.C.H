import time

import pandas as pd
import sklearn
import xgboost


def training_and_predict(dataframe):
    dataframe = dataframe.set_index('CRS_DEP_TIME')
    dataframe['DEP_DELAY'] = dataframe['DEP_DELAY'].astype('int32')

    timer_start: float = time.perf_counter()
    making_targets(dataframe)
    X = dataframe.drop(["CANCELLED", "target-delay"], axis=1)
    y_delay = dataframe["target-delay"]
    y_cancel = dataframe["CANCELLED"]
    # print(X, y)
    X_train, X_test, y_delay_train, y_delay_test = sklearn.model_selection.train_test_split(X, y_delay, test_size=0.3,
                                                                                            random_state=2303)
    _, _, y_cancel_train, y_cancel_test = sklearn.model_selection.train_test_split(X, y_cancel, test_size=0.3,
                                                                                   random_state=2303)
    model_cancel = xgboost.XGBClassifier()
    model_delay = xgboost.XGBClassifier()
    model_cancel.fit(X_train, y_cancel_train)
    y_cancel_prediction_сlass = model_cancel.predict(X_test)
    y_cancel_prediction_proba = model_cancel.predict_proba(X_test)

    model_delay.fit(X_train, y_delay_train)

    y_delay_prediction_class = model_delay.predict(X_test)
    y_delay_prediction_proba = model_delay.predict_proba(X_test)

    all_time: float = time.perf_counter() - timer_start

    print(f"Точность предсказания отмены: {sklearn.metrics.accuracy_score(y_cancel_test, y_cancel_prediction_сlass)}")
    print(f"Точность предсказания задержки: {sklearn.metrics.accuracy_score(y_delay_test, y_delay_prediction_class)}")

    print(f"Время работы модели: {all_time}\n")

    y_cancel_df = pd.DataFrame(y_cancel_prediction_proba,
                               columns=['probability_of_no_cancel', 'probability_of_cancel'])
    y_cancel_df = y_cancel_df['probability_of_cancel']
    y_delay_df = pd.DataFrame(y_delay_prediction_proba, columns=['probability_of_no_delay', 'probability_of_delay'])
    y_delay_df = y_delay_df['probability_of_delay']

    final_column = ['CRS_DEP_TIME', 'AIR_TIME', 'DISTANCE', 'probability_of_cancel', 'probability_of_delay']
    X_test.reset_index(inplace=True)
    final_data = pd.concat([X_test, y_cancel_df, y_delay_df], axis=1)
    final_data = final_data[final_column]
    final_data['probability_of_cancel'] = round(final_data['probability_of_cancel'] * 100, 2)
    final_data['probability_of_delay'] = round(final_data['probability_of_delay'] * 100, 2)

    convert_to_procent(final_data, 'probability_of_cancel')
    convert_to_procent(final_data, 'probability_of_delay')

    print(final_data)


def making_targets(dataframe):
    dataframe["target-delay"] = dataframe["DEP_DELAY"].apply(lambda x: 1 if (x >= 60) or (x == -999) else 0)


def convert_to_procent(dataframe, column):
    dataframe[column] = dataframe[column].apply(lambda x: '< 0.01%' if x < 0.01 else f'{x}%')
