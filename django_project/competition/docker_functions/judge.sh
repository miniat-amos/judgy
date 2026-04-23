#!/bin/bash

problem_name="$1"
compile_cmd="$2"
run_cmd="$3"

user_submission_file="${@: -1}"

output_dir="/app/output"
score_file="$output_dir/score.txt"
output_file="$output_dir/output.txt"

problem_dir="/app/$problem_name"

export JUDGY_SOURCE_FILE="$user_submission_file"

function prep_directory() {
    mkdir -p "$problem_dir"
    cp -r /app/judging/. "$problem_dir"
    cp -r /app/others/. "$problem_dir"
    cp -r /app/submission/. "$problem_dir"
    cd "$problem_dir"

}

function compile() {
    echo "Compiling..."
    eval "$compile_cmd" 2> "$output_file"
    status=$?
    if [ $status -ne 0 ]; then 
     echo "Compiling Failed"
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
    output=$(timeout 60s bash -c "python3 judge.py $run_cmd")

    status=$?; 
    if [ $status -eq 124 ]; then 
      echo "Your program timed out"
    elif [ $status -ne 0 ]; then 
      echo "Runtime error"
    else
        score="${output%% *}"
        filepath="${output#* }"

        echo "$score" > "$score_file"
        cat "$filepath" > "$output_file"
    fi

}

prep_directory
judge