redis-server&
sudo service nginx start
sudo service nginx status
sudo service nginx restart

cd 4/server
node server3000.js &
node server3001.js &

wait