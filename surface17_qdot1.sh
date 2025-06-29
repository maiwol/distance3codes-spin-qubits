#!/bin/bash

declare -i mx=8

for x1 in $(seq 0 1 $mx)
do
  for x2 in $(seq 0 1 $((mx-x1)))
  do  
    for x3 in $(seq 0 1 $((mx-x1-x2)))
    do  
      for x4 in $(seq 0 1 $((mx-x1-x2-x3)))
      do  
        for x5 in $(seq 0 1 $((mx-x1-x2-x3-x4)))
        do  
          for x6 in $(seq 0 1 $((mx-x1-x2-x3-x4-x5)))
          do
            for x7 in $(seq 0 1 $((mx-x1-x2-x3-x4-x5-x6)))
            do
              for x8 in $(seq 0 1 $((mx-x1-x2-x3-x4-x5-x6-x7)))
              do
		echo $x1 $x2 $x3 $x4 $x5 $x6 $x7 $x8      
                time python2.7 QEC_d3_surface17_MC_fast_qdot1.py 7000 12 $x1 $x2 $x3 $x4 $x5 $x6 $x7 $x8 surface17 X
              done
            done
          done
        done
      done
    done
  done
done
    

