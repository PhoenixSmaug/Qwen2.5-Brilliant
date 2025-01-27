# Qwen2.5-Brilliant

This is an experimental notebook to finetune the LLM Qwen2.5-1.5B developed by Alibaba. An overview over its technical details can be found in this [blogpost](https://qwenlm.github.io/blog/qwen2.5/).

The dataset is mined from the Brilliant.org community forum, which allowed users to post their own mathematical problems. After it was shut down in 2021, the Vice President of Brilliant posted a dump of the website [online](https://www.reddit.com/r/DataHoarder/comments/o0qrey/comment/h1zerf6/). The script `data-mining.py` extracts the question and numerical answer to 45k problems from the 10 GB dump, filtering out problems which rely on image context. To provide the model with a proper problem and not simply the numerical solution, it also extracts the content of the most upvoted comment for each problem. While this works in many cases, this rather unreliable method leads to a low quality dataset. But human moderation of the whole dataset is infeasible for an individual project.

The completed dataset is uploaded as `brilliant-community.csv`, which is used by `finetune.ipynb` to train the model. It should be noted that a dedicated GPU with CUDA support is required and with my Nvida GTX 2080 Super the training takes a few hours. For this reason the finished weights are also available in `qwen-brilliant-1.5B`, allowing users to directly load the model from disk.

(c) Mia Müßig