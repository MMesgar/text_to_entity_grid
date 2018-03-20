# Introduction:

This project mainly uses the "Stanford parser" and the "Browncoherence Toolkit". 
The "main.py" script sequentially processes sample texts in the "txt" folder and extracts entity grid representation of each of them. 
The "prs" folder contains corresponding files with text files in the "txt" folder. 
Each sentences of a text file is parsed and its parse tree is saved in a line of the corresponding .prs file in the "prs" folder. 
The "grids" folder contains grid files.

# Run:
1- Installing "Browncoherence Toolkit" is tricky, and may take some time. 
I provided a Docker image that makes this process faster. As the first step, take this image from 
[here](https://cloud.docker.com/swarm/mmesgar/repository/docker/mmesgar/text_to_egrid) in Docker Hub:

$ docker pull mmesgar/text_to_egrid

2- run the Docker image and share the "text_to_entity_grid" folder with it

$ docker run -it  -v  $PWD/text_to_entity_grid/:/root/text_to_entity_grid/  mmesgar/text_to_egrid

3- run the code in the container

$ cd /root/text_to_entity_grid/

$ python main.py


# What is setup.ipynb?
Just in case, if you are curious to know how I installed BrownCoherence Toolkit, this notebook provides a step by step explanation of this. 

# Different versions of entity grids?
The original entity grid model applies head string match over noun phrases. In another version, it applies string match over all nouns. 
To get the output of each version, you need to change some lines in ~/browncoherence/src/Sent.cc file.

There is one block in Sent.cc that is annotated with "--mention--". It is commented out now by /\* block \*/.
In this situation, the model is in its original setting, head string match over NPs. 
If you like to use all nouns as mentions, remove /\* and \*/. 
Don't forget to compile the toolkit by 

$ cd ~/browncoherence

$ make everything

