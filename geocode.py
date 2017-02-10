from src.db import AddressDatabase
from src.geocode import batch

db = AddressDatabase()
batch(db, 'data/Listing Adresse Ptf total.csv',
      'Listing Adresse Ptf total auto.csv')
