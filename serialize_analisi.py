import pandas as pd
import numpy as np
import math
import json
import gzip
import jsonlines


def write_jsonlines(df, filename):
    with jsonlines.open(filename, mode='w') as writer:
        for record in df.to_dict(orient='records'):
            writer.write(record)

def write_json_in_chunks(df, filename, chunk_size=1000):
    with open(filename, 'w') as f:
        f.write('[\n')
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i + chunk_size]
            chunk_json = chunk.to_json(orient='records', lines=True).splitlines()
            chunk_json = ',\n'.join(chunk_json)
            if i + chunk_size < len(df):
                chunk_json += ',\n'
            f.write(chunk_json)
            print(f"write { i/len(df)}")
        f.write('\n]')


# Read the Excel file
file_path = 'exp_analisi2024.xlsx'  # Replace with the path to your Excel file
#file_path = 'singolo_prezzo.xlsx'
df = pd.read_excel(file_path, header=None)  # Read without header

main_price = pd.DataFrame(columns=['Codice', 'Ex-Codice', 'Descrizione', 'SUB', 'Totale', 'SGEUI', 'ITU'])
sub_price = pd.DataFrame(columns=['Codice', 'Ex-Codice', 'Descrizione', 'Qta', 'UMI', 'IU', 'Importo'])
new_row = {}
nuova_riga = False

for index, row in df.iterrows():
#    if index == 8000:
#        break
    if row.isnull().all():
        nuova_riga = True
        new_row = {}
        continue
        
    # Convert row to list for easy access
    row_data = row.tolist()
    
    if row_data[0] == 'Analisi prezzi: Prezzario 2024':
        continue

    
    elif isinstance(row_data[6], float) or isinstance(row_data[6], int):
        if math.isnan(float(row_data[6])):
            new_row["Codice"] = row_data[0]
            new_row["Ex-Codice"] = row_data[1]
            new_row["Descrizione"] = row_data[2]
            #print(f"Row {index+1} is a main row: {row_data}")
    
        if row_data[0] == 'TOTALE:':
            new_row["Totale"] = row_data[6]
            #print(f"Row {index+1} is a total row: {row_data}")

        if row_data[0] == 'IMPORTO TOTALE UNITARIO:':
            new_row["ITU"] = row_data[6]
            nuova_riga = False
            #print(f"Row {index+1} is an ITU row: {row_data}")
                        
        if row_data[0] == "SPESE GENERALI E UTILE D'IMPRESA:" and (row_data[5] == 0.265 or row_data[5] == 0):
            new_row["SGEUI"] = row_data[6]
            #print(f"Row {index+1} is an SGEU row: {row_data}")
            
        # Store the data in the dictionary
        if isinstance(row_data[4], str):
            sub_price=sub_price._append({
                "Codice" : row_data[0],
                "Ex-Codice" : row_data[1],
                "Descrizione" : row_data[2],
                "Qta" : row_data[3],
                "UMI" : row_data[4],
                "IU" : row_data[5],
                "Importo" : row_data[6],
                }, ignore_index=True)
            
            new_row["SUB"] = sub_price
            
    elif row_data[0] == "Codice":
        continue
#        print(f"Row {index+1} is a title row: {row_data}")

    if nuova_riga == False:
        main_price = main_price._append(new_row, ignore_index=True)

print()
# Print the dictionary to verify
#print(main_price["Totale"])
#print(main_price.columns)
#print(main_price.head(5))
      
#print(sub_price)

# Save to Json
#main_price.to_json('exp_analisi2024.json', orient='records', indent=4, default_handler=str)

#main_price.to_json('exp_analisi2024.json', orient='records', compression={'method': 'gzip', 'compresslevel': 1, 'mtime': 1})

#with gzip.open('main_price.json.gz', 'wt', encoding='utf-8') as f:
#    main_price.to_json(f, orient='index', lines=True)

#with gzip.open('main_price.json.gz', 'wt', encoding='utf-8') as f:
#    main_price.to_json(f, orient='index')

#write_json_in_chunks(main_price, "exp_analisi2024.json")
write_jsonlines(main_price, "exp_analisi2024.json")

#with open('data_dict.json', 'w') as file:
#    json.dump(data_dict, file)

# read the Json
#with open('singolo_prezzo.json', 'r') as file:
#    data = json.load(file)

#table = pd.read_json('exp_analisi2024.json', orient='records')

#sub_table = table[table["Codice"] == "VEN24-AT.09.01.a"]["SUB"].iat[0]
#sub_table = pd.DataFrame.from_records(sub_table)

#sub_table = table[pd.isna(table["ITU"])]

#sub_table.to_excel("prova.xlsx")
#print(sub_table)
