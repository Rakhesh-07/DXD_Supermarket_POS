import pickle
with open ("bill_details.dat","rb") as fp:
    a=pickle.load(fp)
    print(a)
