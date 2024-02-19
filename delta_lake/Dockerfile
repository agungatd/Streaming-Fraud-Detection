FROM deltaio/delta-docker:latest 

# Set a working directory for your project
WORKDIR /opt/spark/work-dir

# Copy requirements file into the container
COPY requirements.txt /opt/spark/work-dir 

# Install dependencies
RUN pip install -r /opt/spark/work-dir/requirements.txt  
