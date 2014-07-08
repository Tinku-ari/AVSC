from kaggleShopper import *

if __name__=="__main__":
       data_dir= 'data/'
       train_file= 'trainHistory.csv'
       test_file= 'testHistory.csv'
       offer_file= 'offers.csv'
       transaction_file= 'transactions.csv'

       trainhist_offers_file= 'trainhist_offers.csv'
       reduced_transaction_file= 'reduced1.csv'
       reduced_dated= 'reduced-dated1.csv'
       transaction_aggr_file= 'transactions-aggr.csv'
       trainhist_offers_transaction_file= 'trainhist_offers_transaggr1.csv'

       testhist_offers_file= 'testhist_offers.csv'
       testhist_offers_transaction_file= 'testhist_offers_transaggr1.csv'

       model_choice=[linear_model.LogisticRegression(),GaussianNB(),svm.SVC(),
                     ExtraTreesClassifier(n_estimators=50), AdaBoostClassifier(n_estimators=50),
                     GradientBoostingClassifier()]
       dense_model= [1,2]
       model = model_choice[0]
       date_to_split_begin= '04-01-2013'
       date_to_split_end= '04-20-2013'
       case= None
       add_data=None
       best_c=None

       An=AnalyzePredict(data_dir,date_begin=date_to_split_begin, date_end=date_to_split_end)
       # read train
       An.read_aggr_data(file=trainhist_offers_transaction_file, case='train')
       # read test
       An.read_aggr_data(file=testhist_offers_transaction_file, case='test')
       # normalize the data
       data_aggr_scaled = An.normalize_data(add_data, case='train')
       print data_aggr_scaled.shape,An._trainresponse.shape




