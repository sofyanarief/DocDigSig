#!/bin/bash

data=("Supriatna Adhisuwignjo, S.T., M.T.	Direktur	197101081999031001"
"Dr. Dra. Kurnia Ekasari, Ak., M.M., CA.	Wakil Direktur Bidang I	196602141990032002"
"Jaswadi, SE., M.Si., DBA.Ak.C	Wakil Direktur Bidang II	197711081999031003"
"Dr.Eng. Anggit Murdani, S.T., M.Eng	Wakil Direktur Bidang III	197109151999031001"
"Ratih Indri Hapsari, S.T., M.T., Ph.D.	Wakil Direktur Bidang IV	197703062002122001"
"Andi Kusuma Indrawan, S.Kom., M.T.	Kepala UPA TIK	197806292005011002"
"Dr. Ratna Ika Putri, S.T., M.T.	Kepala Pusat P3M	197710222000122001")

# Inisialisasi array untuk setiap elemen
names=()
positions=()
nips=()

# Loop untuk memisahkan setiap data menjadi elemen array
for line in "${data[@]}"; do
  # Menggunakan IFS (Internal Field Separator) untuk memisahkan berdasarkan tab
  IFS=$'\t' read -r name position nip <<< "$line"
  
  # Menambahkan ke array yang sesuai
  names+=("$name")
  positions+=("$position")
  nips+=("$nip")
done

# Loop untuk menambahkan user001 hingga user100
for i in $(seq 1 100); do
    for t in $(seq 1 6); do
        json=$(printf '{"key_name": "%s", "key_position": "%s", "key_other_info": "%s", "t_user_id_user": %d}' "${names[$t]}" "${positions[$t]}" "${nips[$t]}" "$i")
        echo $json
        # response=$(curl http://localhost:5000/keys -X POST -H "Content-Type: application/json" -d '{"key_name": "'$(echo ${names[$t]})'", "key_position": "'$(echo ${positions[$t]})'", "key_other_info": "'$(echo ${nips[$t]})'", "t_user_id_user": '$i'}')
        response=$(curl http://localhost:5000/keys -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d "$json")

        # Cek status code dari response
        if [ "$response" -eq 201 ]; then
            echo "Key $t for user $i added successfully!"
        else
            echo "Failed to add key $t for user $i. Status code: $response"
        fi
            sleep 1
    done
    echo "----------------------------------------------------------------------"
    sleep 3
done