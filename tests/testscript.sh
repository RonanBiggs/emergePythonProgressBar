#!/bin/bash

echo "=== Running Test 1 ==="
./fakeEmerge.sh test1.txt | python ../main.py
echo "Press any key to continue..."
read -n 1

echo "=== Running Test 2 ==="
./fakeEmerge.sh test2.txt | python ../main.py
echo "Press any key to continue..."
read -n 1

echo "=== Running Test 3 ==="
./fakeEmerge.sh test3.txt | python ../main.py

echo "=== All tests completed ==="
