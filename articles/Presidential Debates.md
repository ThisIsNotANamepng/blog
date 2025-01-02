Politics
# Presidential Debates

I think we all know that the first 2024 US presidential election debate was a [little wacky](https://www.theguardian.com/us-news/article/2024/jun/27/fact-check-debate-biden-trump). This got me thinking about past presidential debates, which apparently have an [interesting history](https://www.debates.org/debate-history/). I wanted to measure the topics brought up by each candidate and compare them to the topics the audience wanted to hear about, but it mainly turned into a generic NLP analysis of all of the presidential debates since 1960.

I got the transcripts for debates 1960-2020 from [https://www.kaggle.com/datasets/bahdahshin/presidential-debates](https://www.kaggle.com/datasets/bahdahshin/presidential-debates), it included video files for each debate as well which I didn't need, so I re-released the dataset [here](https://www.kaggle.com/datasets/jackhagen/us-presidential-debate-transcripts-text-only) with only the text transcripts. I didn't change anything else except some file structure.

This is a living document, I'll probably add more later, but for now it's a basic sentiment analysis of all debates 1960-2020 (I'll add the 2024 debates when all of them are finished).

## Sentiment Analysis

I used `nltk`'s inbuilt `SentimentIntensityAnalyzer` to gauge the sentiment of the debates (after cleaning the text). Here's the sentiment analysis chart (meausred by negative, neutral, and positive sentiment). 

![A Sentiment Analysis Chart of US Presidential Debates](/static/DebateSentiments.png "A Sentiment Analysis Chart of US Presidential Debates")

Sometime in the future I will probably do more analysis, and analyze why they had the characteristics that they did.