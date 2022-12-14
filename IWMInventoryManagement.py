import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sys, requests, json
from json import JSONDecodeError


@st.cache
def generate_token(username, password):
	header = {
        "username":username,
        "password": password
    }

	res = requests.post('https://mamazon.zefresk.com/auth.php', data=header)
	return res


def main():
	st.title("Mamazon PrimeAir Inventory Management")

	# Create an empty container


	if 'res' not in locals():
		placeholder = st.empty()
		with placeholder.form("login"):
		    st.markdown("#### Enter your credentials")
		    username = st.text_input("Username")
		    password = st.text_input("Password", type="password")
		    submit = st.form_submit_button("Login")
		res = generate_token(username, password)


	if res.status_code == 200:
		placeholder.empty()
		#st.success("Connexion réussie")
		#st.title("Mamazon PrimeAir Inventory Management")


		TOKEN = res.text
		URL = "https://mamazon.zefresk.com/query.php"

		# Warehouse Section
		DATA = { 'code': 3,
           'token': TOKEN,
           'content': {}}

		r = requests.post(url = URL, json = DATA)
		answer = r.json()
		Warehouse = answer["content"]["list"]
		choose_warehouse = st.sidebar.selectbox("Choose the warehouse", Warehouse)

		DATA2 = { 'code': 5,
           'token': TOKEN,
           "content": {
	           "location": {
	               "warehouse": choose_warehouse,
	               "allee": "*",
	               "travee": "*",
	               "niveau": "*",
	               "alveole": "*"
	           },
	           "product": "*"}}


		r2 = requests.post('https://mamazon.zefresk.com/query.php',json=DATA2)
		item_list = r2.json()['content']['list']
		choose_item = st.sidebar.selectbox("Select the item", options=[item["name"] for item in item_list])



		st.write("The location and quantity of ", choose_item, "in ", choose_warehouse, " :")

		for i in range(len(item_list)):
			if (item_list[i]["name"] == choose_item) :
				pos = i

		df = pd.json_normalize(item_list[pos])
		df = df.rename(index={0: "Product details"})
		st.write(df.T)


		# Adjustment Section
		st.subheader("Stock Adjustment")


		choose_adj = st.sidebar.selectbox("Do you want to adjust the stock",["NO", "YES"])

		if(choose_adj == "NO"):
			st.write("No adjustment is possible")
		elif(choose_adj == "YES"):
			# Adjustment form
			my_form = st.form(key = "adj_form")
			new_qty = my_form.number_input(label = "Enter the new quantity", format="%d", step=1)
			submit = my_form.form_submit_button(label = "Adjust")

			if submit :
				DATA3 = {
                    "code": 7,
                    "token": TOKEN,
                    "content": {
                        "location": {
                            "warehouse": item_list[pos]["location"]["warehouse"],
                            "allee": item_list[pos]["location"]["allee"],
                            "travee": item_list[pos]["location"]["travee"],
                            "niveau": item_list[pos]["location"]["niveau"],
                            "alveole": item_list[pos]["location"]["alveole"]
                            },
                        "product": item_list[pos]["code"],
                        "quantity": new_qty
                    }
                }
				res4 = requests.post('https://mamazon.zefresk.com/query.php',json=DATA3)
				try :
					if res4.json()["content"]["success"] == 1 :
						st.success("Adjustment Done !")

				except JSONDecodeError as e:
					st.error('You are trying to remove more than the available stock', icon="🚨")
				else :
					time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
					#old_qty = df.loc[(df["Warehouse"]==choose_warehouse) & (df["Item"]==choose_item)]['Quantity']
					#adj_nb = int(old_qty - new_qty)
					#if adj_nb>=0:
						#adj_nb='+'+str(adj_nb)
					#else :
						#adj_nb=str(adj_nb)
						#log = time+" Adjustment of "+adj_nb+" for "+choose_item+" in "+choose_warehouse
						#with open('log.txt', 'a+') as f:
							#f.write(log+'\n')
							#f.close()

	else:
	    st.error("Login failed")

		# TO DO :
		# Gérer la cnx avec la bdd
		# Récupérer la liste des warehouses depuis la bdd
		# Récupérer la liste des items pour le warehouse sélectionné
		# Adapter le formulaire pour l'envoie de la requête d'adjustment

		# Afficher un msg de succès/erreur après l'envoie de la requête
		# Ajouter un affichage des log (read du fichier) (case à cocher ?)




if __name__ == "__main__":
	main()
