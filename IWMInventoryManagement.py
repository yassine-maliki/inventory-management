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
           'content': {"type": "warehouse"}}

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


		df_items = pd.json_normalize(np.array(item_list))
		unique_item_list = df_items["name"].unique()

		choose_item = st.sidebar.selectbox("Select the item", options=[item for item in unique_item_list])
		grouped_items = df_items.loc[df_items["name"] == choose_item].sort_values("quantity", ascending=False).reset_index(drop=True)
		grouped_items_new = grouped_items.drop(columns = ["name", "location.warehouse"])



		st.write("The locations and quantities of ", choose_item, "in ", choose_warehouse, " :")
		st.write(grouped_items_new)


		# Adjustment Section
		st.subheader("Stock Adjustment")


		choose_adj = st.sidebar.selectbox("Do you want to adjust the stock",["NO", "YES"])

		if(choose_adj == "NO"):
			st.write("No adjustment is possible")
		elif(choose_adj == "YES"):
			# Adjustment form
			my_form = st.form(key = "adj_form")

			index_value = my_form.selectbox("Choose the index of the article to adjust", grouped_items.index.tolist())
			adj = my_form.number_input(label = "Enter the quantity to add (+) or to remove (-)", format="%d", step=1)
			submit = my_form.form_submit_button(label = "Adjust")

			if submit :
				DATA3 = {
                    "code": 7,
                    "token": TOKEN,
                    "content": {
                        "location": {
                            "warehouse": grouped_items.at[index_value, "location.warehouse"],
                            "allee": grouped_items.at[index_value,"location.allee"],
                            "travee": grouped_items.at[index_value,"location.travee"],
                            "niveau": grouped_items.at[index_value,"location.niveau"],
                            "alveole": grouped_items.at[index_value,"location.alveole"]
                            },
                        "product": grouped_items.at[index_value,"code"],
                        "quantity": adj
                    }
                }
				res4 = requests.post('https://mamazon.zefresk.com/query.php',json=DATA3)
				try :
					if res4.json()["content"]["success"] == 1 :
						st.success("Adjustment Done !")
						DATA6 = { 'code': 5,
				           'token': TOKEN,
				           "content": {
					           "location": {
					               "warehouse": grouped_items.at[index_value, "location.warehouse"],
					               "allee": grouped_items.at[index_value,"location.allee"],
					               "travee": grouped_items.at[index_value,"location.travee"],
					               "niveau": grouped_items.at[index_value,"location.niveau"],
					               "alveole": grouped_items.at[index_value,"location.alveole"]
					           },
					           "product": grouped_items.at[index_value,"code"]}}


						r6 = requests.post('https://mamazon.zefresk.com/query.php',json=DATA6)
						updated_item = r6.json()['content']['list']
						updated_item_df = pd.json_normalize(np.array(updated_item))
						updated_item_df.drop(columns = ["name", "location.warehouse"] , inplace=True)
						st.write(updated_item_df)




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


if __name__ == "__main__":
	main()
