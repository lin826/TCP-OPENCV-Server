while :
do
    python3.11 client.py --host $1
    echo "Retrying in 120 secs"
    sleep 120
done