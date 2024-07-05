import pandas as pd
import math

file_path_elenco = 'exp_elenco2024.xlsx'
file_path_analisi = 'exp_analisi2024.xlsx'

df_elenco = pd.read_excel(file_path_elenco, header=None)
df_analisi = pd.read_excel(file_path_analisi, header=None)

elenco_prezzi = pd.DataFrame(columns=['Codice', 'Ex-Codice', 'Descrizione', 'UMI', 'Prezzo', 'PercMan'])
df_elenco = df_elenco.drop(df_elenco.index[[1,2]])

analisi_prezzi = pd.DataFrame(columns=['Codice', 'Ex-Codice', 'Descrizione', 'SUB', 'Totale', 'SGEUI', 'ITU'])
sub_price = pd.DataFrame(columns=['Codice', 'Ex-Codice', 'Descrizione', 'Qta', 'UMI', 'IU', 'Importo'])


#iter analisi
new_row = {}
nuova_riga = False
for index, row in df_analisi.iterrows():
#    if index == 8000:
#        break
    if row.isnull().all():
        nuova_riga = True
        sub = []
        new_row = {}
        continue
        
    # Convert row to list for easy access
    row_data = row.tolist()
    
    if row_data[0] == 'Analisi prezzi: Prezzario 2024':
        continue
    
    elif isinstance(row_data[6], float) or isinstance(row_data[6], int):
        if math.isnan(float(row_data[6])):
            new_row["Codice"] = row_data[0]
#            new_row["Ex-Codice"] = row_data[1]
#            new_row["Descrizione"] = row_data[2]
    
        if row_data[0] == 'TOTALE:':
            continue
#            new_row["Totale"] = row_data[6]

        if row_data[0] == 'IMPORTO TOTALE UNITARIO:':
#            new_row["ITU"] = row_data[6]
            nuova_riga = False
                        
        if row_data[0] == "SPESE GENERALI E UTILE D'IMPRESA:" and (row_data[5] == 0.265 or row_data[5] == 0 or row_data[5] == 0.15):
#            continue
            new_row["SGEUI"] = row_data[5]
            
        # Store the data in the dictionary
        if isinstance(row_data[4], str):
            sub.append(row_data[0])
            
#            sub_price = sub_price._append({
#                "Codice" : row_data[0],
#                "Ex-Codice" : row_data[1],
#                "Descrizione" : row_data[2],
#                "Qta" : row_data[3],
#                "UMI" : row_data[4],
#                "IU" : row_data[5],
#                "Importo" : row_data[6],
#                }, ignore_index=True)
            
#            new_row["SUB"] = sub_price["Codice"].tolist()
            
    elif row_data[0] == "Codice":
        continue

    if nuova_riga == False:
        new_row["SUB"] = sub 
        #analisi_prezzi = analisi_prezzi._append(new_row, ignore_index=True)
        analisi_prezzi = analisi_prezzi._append(new_row, ignore_index=True)

#analisi_prezzi.to_json('exp_analisi2024.json', orient='records', indent=4, default_handler=str)


print("Finito analisi prezzi")

new_row = {}
for index, row in df_elenco.iterrows():
    row_data = row.tolist()
    if math.isnan(float(row_data[4])):
        continue
    
    new_row["Codice"] = row_data[0]
    new_row["Ex-Codice"] = row_data[1]
    new_row["Descrizione"] = row_data[2]
    new_row["UMI"] = row_data[3]
    new_row["Prezzo"] = row_data[4]
    new_row["PercMan"] = row_data[5]
    #new_row["SUB"] = analisi_prezzi[ analisi_prezzi["Codice"] == new_row["Codice"] ]["SUB"].iat[0]["Codice"]
    if not analisi_prezzi[ analisi_prezzi["Codice"] == new_row["Codice"] ]["SUB"].empty:
        new_row["SUB"] = analisi_prezzi[ analisi_prezzi["Codice"] == new_row["Codice"] ]["SUB"]
        new_row["SGEUI"] = analisi_prezzi[ analisi_prezzi["Codice"] == new_row["Codice"] ]["SGEUI"]
#        print(new_row["SUB"])
#    print(new_row["Codice"])
    #print(analisi_prezzi[ analisi_prezzi["Codice"] == new_row["Codice"] ]["SUB"])
#    print(analisi_prezzi["Codice"])

    elenco_prezzi = elenco_prezzi._append(new_row, ignore_index=True)
    new_row = {}

print()

#print(analisi_prezzi[ analisi_prezzi["Codice"=="VEN24-AT.09.01.a"]["Descrizione"] ])
#print(analisi_prezzi[analisi_prezzi["Codice"] == "VEN24-AT.09.01.a"] ["SUB"])

#print(elenco_prezzi[elenco_prezzi["Codice"] == "VEN24-AT.09.01.c"]["SUB"])

print(elenco_prezzi[elenco_prezzi["Codice"] == "VEN24-21.02.14.a"]["SUB"])
print(elenco_prezzi[elenco_prezzi["Codice"] == "VEN24-21.02.14.a"]["SGEUI"])

elenco_prezzi.to_json('exp_elenco2024.json', orient='records', indent=4, default_handler=str)








