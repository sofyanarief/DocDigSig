#!/bin/bash

arrkeyidentity=(
  [0,0]="Supriatna Adhisuwignjo, S.T., M.T." [0,1]="Direktur" [0,2]="197101081999031001"
  [1,0]="Dr. Dra. Kurnia Ekasari, Ak., M.M., CA." [1,1]="Wakil Direktur Bidang I" [1,2]="196602141990032002"
  [2,0]="Jaswadi, SE., M.Si., DBA.Ak.C" [2,1]="Wakil Direktur Bidang II" [2,2]="197711081999031003"
  [3,0]="Dr.Eng. Anggit Murdani, S.T., M.Eng" [3,1]="Wakil Direktur Bidang III" [3,2]="197109151999031001"
  [4,0]="Ratih Indri Hapsari, S.T., M.T., Ph.D." [4,1]="Wakil Direktur Bidang IV" [4,2]="197703062002122001"
  [5,0]="Andi Kusuma Indrawan, S.Kom., M.T." [5,1]="Kepala UPA TIK" [5,2]="197806292005011002"
  [6,0]="Dr. Ratna Ika Putri, S.T., M.T." [6,1]="Kepala Pusat P3M" [6,2]="197710222000122001"
)

# Dapatkan semua kunci array yang mengandung elemen baris (indeks pertama)
keys=("${!arrkeyidentity[@]}")

# Ambil jumlah unik baris dengan menghitung bagian sebelum koma
rows=$(for key in "${keys[@]}"; do echo "$key" | cut -d',' -f1; done | sort -nu)

# Loop untuk menambahkan user001 hingga user100
for i in $(seq -w 1 100); do
    for t in $rows; do
        response=$(curl http://localhost:5000/keys -X POST -H "Content-Type: application/json" -d '{"key_name": "'${arrkeyidentity[$t,0]}'", "key_position": "'${arrkeyidentity[$t,1]}'", "key_other_info": "'${arrkeyidentity[$t,2]}'", "t_user_id_user": '$i'}')

        # Cek status code dari response
        if [ "$response" -eq 201 ]; then
            echo "Key $t for user $i added successfully!"
        else
            echo "Failed to add key $t for user $i. Status code: $response"
        fi
    done
done