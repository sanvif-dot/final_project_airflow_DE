# final_project_airflow_DE

Project ini membuat data warehouse (postgresql) dari data yelp academic (json) dan climate data (csv) 
menggunakan airflow yang terpasang pada docker

Tujuan project ini untuk mengetahui korelasi data climate (temperature dan precipitation) dengan review restauran

Hasilnya dimodelkan menggunakan TOOLS GRAFANA sebagai berikut

![precipitation score](https://user-images.githubusercontent.com/122470555/227584785-5e7601d6-dcbc-406c-acd5-6be73c8411e5.png)
![temperature score](https://user-images.githubusercontent.com/122470555/227584798-ce6fdfb6-0954-4be6-9034-2c5dfbd95f80.png)



Terlihat bahwa pengunjung lebih menyukai restauran pada temperature tinggi dengan jumlah bintang/review sebanyak 70 dan 
pada precipitation tinggi sebesar 2.31 dengan jumlah bintang 1205
