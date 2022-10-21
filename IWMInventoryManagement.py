import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import csv
import sys

@st.cache
def loadDf():
	df = pd.read_csv("Mamazon.csv", sep=";")
	return df


def main():
	st.title("Mamazon PrimeAir Inventory Management")
	df = loadDf()
	Warehouse = ["NONE"]+df["Warehouse"].unique().tolist()


	# Warehouse Section
	choose_warehouse = st.sidebar.selectbox("Choose the warehouse", Warehouse)
	item_list = ["NONE"]+df.loc[df["Warehouse"]==choose_warehouse]['Item'].tolist()
	choose_item = st.sidebar.selectbox("Select the item", options=[opt.strip() for opt in item_list])
	choose_adj = st.sidebar.selectbox("Do you want to adjust the stock",["NO", "YES"])

	if(choose_warehouse != "NONE" and choose_item != "NONE"):

		st.write("The location and quantity of ", choose_item, "in ", choose_warehouse, " :")
		st.write(df.loc[(df["Warehouse"]==choose_warehouse) & (df["Item"]==choose_item)])
		# Adjustment Section
		st.subheader("Stock Adjustment")


		if(choose_adj == "NO"):
			no_adj = '<p style="font-family:sans-serif; color:RED; ">No adjustment is possible</p>'
			st.markdown(no_adj, unsafe_allow_html=True)
		elif(choose_adj == "YES"):
			# Adjustment form
			my_form = st.form(key = "adj_form")
			new_qty = my_form.number_input(label = "Enter the new quantity", format="%d", step=1)
			submit = my_form.form_submit_button(label = "Adjust")

			if submit : # Succes msg + write logs
				st.success("Adjustment Done !")
				time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
				old_qty = df.loc[(df["Warehouse"]==choose_warehouse) & (df["Item"]==choose_item)]['Quantity']
				adj_nb = int(old_qty - new_qty)

				if adj_nb>=0:
					adj_nb='+'+str(adj_nb)
				else :
					adj_nb=str(adj_nb)

				#log = time+" Adjustment of "+adj_nb+" for "+choose_item+" in "+choose_warehouse
				log = [time, adj_nb, choose_warehouse, choose_item]
				with open('log.csv', 'a+') as f:
					writer = csv.writer(f)
					#header = ['Date', 'Adjustment', 'Warehouse', 'Item']
					#writer.writerow(header)
					writer.writerow(log)

		# Affichage des logs
		if st.checkbox("Show adjustment log"):
			log_df = pd.read_csv("log.csv", sep=",")
			log_df
	else:
		attention = '<p style="font-family:sans-serif; color:RED; font-size: 22px;">First choose a Warehouse and an item !</p>'
		st.markdown(attention, unsafe_allow_html=True)


		# TO DO :
		# Gérer la cnx avec la bdd
		# Récupérer la liste des warehouses depuis la bdd
		# Récupérer la liste des items pour le warehouse sélectionné
		# Adapter le formulaire pour l'envoie de la requête d'adjustment

		# Afficher un msg de succès/erreur après l'envoie de la requête
		# Ajouter un affichage des log (read du fichier) (case à cocher ?)




if __name__ == "__main__":
	main()
