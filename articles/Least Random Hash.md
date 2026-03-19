# Least Random Hash

I have a research project involving measuring the entropy of encrypted text (that research will eventually be posted here). As I thought of that I wondered what the least random hash was. No idea why, I just did.

So, naturally, I downloaded the largest wordlist I could find and got to work.

## The Dataset

I used the [Crackstation password dictionary](https://crackstation.net/crackstation-wordlist-password-cracking-dictionary.htm). It is the combination of all of the leaked password that the author could find over the years, as well as all of the words in Wikipedia and books from project Gutenberg. It contains 1,493,677,782 unique strings. 

## The Hashes

I originally wanted to download a rainbow table and find the entropies of all of the hashes from there, but I found that people are picky about releasing their personal database of cracked passwords for some reason. So, I instead downloaded the dataset and wrote a quick python script which hashed (sha256) all of the strings and stored them in a `hashes.txt` file which file numbers corresponds to the dataset .txt file. 

## Entropies

I then wrote a quick python script which went through the hashes file, and found and stored the entropy for each hash in a `entropies.txt` file, again, corresponding the line number with the hash in `hashes.txt`.

## Finding the Least Random

Then came the surprisingly most difficult part, I wrote yet another python script which went through `entropies.txt` and found the 20 smallest values and their line number. This still doesn't work for some reason (I'm working on it), so I wrote a script which just finds the smallest number, not the 20 smallest.  

# Results 

## Round 1

The least random hash, with a `3.1613022383157516` shannon entropy, is `2a22011a710f20462727e22706a17023a579a720702467256f572a7221f03a1a`, which is given by `zHUvtrHG1sE4al`.

The most random hash, with a `3.9943042503656208` shannon entropy, is `95062ef11cdb7d8834edb4583afd2433a0a670015fb2cae994f1768c6e9bc972`, which is given by `22158872`.

## Round 2

The least random hash, with a `3.1508173248304843` shannon entropy, is `434c488cc4bc46c558c2618c241cc8cbbc34c294c8bb6264411ac4bac63a8611`, which is given by `1621ffa0f7fa29a7ab9f4e7b10f425e559f50d243011249d1550d2ff533e4f6d`.

The most random hash, with a `3.9943042503656208` shannon entropy, is `c13d0e55d85eb6b46a622b9dac8741f1a5d84137f987c06f21ec0b04fa3927e3`, which is given by `7501d70672af4e9c803ea50d1955c283838b90ad8a6d66d30e624c2312fbcf0f`.

## Hash Matching

I realized that the hash given by my python script doesn't match the one I get from other tools (sha256sum on Linux, and other online tools). It doesn't really matter because this project doesn't matter, but maybe I'll take a look as to why another time.

## Future work

I found a pretty non-random hash, but I was thinking, I have a dataset of 1.4 billion strings (the hashes I calculated). Why not hash and find the entropy for those? Why not do it again? Why not have it iterate continuously, filling my HPC account storage with multiple large datasets of sha256 hashes? Maybe I will, maybe I won't.

# Acknowledgements

Because of my poorly written code and huge dataset, elements of this projects took as much as 150 GB of RAM, which, alas, I don't have on my laptop. Thankfully, I know how to use [UWEC's High Performance Computing Center](https://hpc.uwec.edu/) (I'm a student system administrator there), so I utlized our BOSE cluster for this work. Therefore, I have to include this acknolegement statement in my research.

>The computational resources of the study were provided by the Blugold Center for High-Performance Computing under NSF grant CNS-1920220.

I also used [OnDemand](https://openondemand.org/) to run and monitor everything, so I have to include this citation as well.

>Hudak et al., (2018). Open OnDemand: A web-based client portal for HPC centers. Journal of Open Source Software, 3(25), 622, https://doi.org/10.21105/joss.00622
