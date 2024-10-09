#!/bin/bash

# Loop untuk menambahkan user002 hingga user100
for i in $(seq -w 2 100); do
    username="user${i}"  # user002, user003, ..., user100
    userpass="12345678"
    user_nickname="User${i}"  # User 002, User 003, ..., User 100
    response=$(curl http://localhost:5000/users -X POST -H "Content-Type: application/json" -d '{"username": "'$username'", "userpass": "'$userpass'", "user_nickname": "'$user_nickname'"}')

    # Cek status code dari response
    if [ "$response" -eq 201 ]; then
        echo "User $username added successfully!"
    else
        echo "Failed to add $username. Status code: $response"
    fi
done