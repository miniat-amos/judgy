
create_virtualenv() {

    sudo apt update
    sudo apt install -y software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa

    sudo apt update
    sudo apt install -y python3.12 python3.12-venv python3.12-dev

    echo "Creating virtual env"

    # Create the python virtual env (USING VERSION 3.12)
    python3.12 -m venv env

    # Activate the environment
    source ./env/bin/activate

    # Install requirements.txt
    pip install --upgrade pip
    pip install -r requirements.txt

}