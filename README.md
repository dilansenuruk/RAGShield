# RAGShield

Creating the environment inside the project directory
>> conda create --prefix ./ragsenv python=3.11 -y

Activate the environment
>> conda activate "D:\git things\RAGShield\ragsenv"

Install the requirements
>> pip install -r requirements.txt

To run frontend
>> cd frontend
>> npm run dev

To export the environment to a yml file
>> conda env export --prefix ./ragsenv > environment.yml

Recreating the environment from yml file
>> conda env create -f environment.yml

Run from the project root to execute the data ingestion pipeline
>> python -m backend.ingest