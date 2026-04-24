#!/bin/bash

problem_name="$1"
compile_cmd="$2"
run_cmd="$3"

user_submission_file="${@: -1}"

score=""
output=""

problem_dir="/sandbox/$problem_name"

export JUDGY_SOURCE_FILE="$user_submission_file"

function prep_directory() {
    mkdir -p "$problem_dir"

    cp -r /app/judging/. "$problem_dir"
    cp -r /app/others/. "$problem_dir"
    cp -r /app/submission/. "$problem_dir"

    echo "" > /app/output/score.txt
    echo "" > /app/output/output.txt

    cd "$problem_dir"
}

function compile() {
    echo "Compiling..."
    output=$(eval "$compile_cmd" 2>&1)
    status=$?
    if [ $status -ne 0 ]; then 
     score="FAILED: Compiling Failed"
     print_vars
     exit 1
    fi
}

function judge() {

    if [[ -n "$compile_cmd" ]]; then
      compile
      echo "Compiling successful"
    else
      echo "Skipping Compiling"
    fi

    echo "Running judging program"
    judge_output=$(timeout 60s bash -c "python3 judge.py $run_cmd")

    status=$?; 
    if [ $status -eq 124 ]; then 
      score="FAILED: Your program timed out"
      output="Your program ran for longer than 60 seconds"
    elif [ $status -ne 0 ]; then 
      score="FAILED: Runtime error"
      output="$judge_output"
    else
      score="${judge_output%% *}"
      output="${judge_output#* }"
    fi

    print_vars

}

function print_vars() {

  echo "$score" > /app/output/score.txt

  if [[ -f "$output" ]]; then
    cat "$output" > /app/output/output.txt
  else
    echo "$output" > /app/output/output.txt
  fi
}


prep_directory
judge
