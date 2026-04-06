tags:Cryptography
date:2024-09-02
# Enhanced Letter Frequencies

Analyzing letter frequencies is a standard tool in breaking rudimentary ciphers. Its a base for people learning cryptography. Usually one would use a classic letter frequency chart such as [https://en.wikipedia.org/wiki/Letter_frequency](https://en.wikipedia.org/wiki/Letter_frequency). 

Charts like this are the results of measuring the frequencies of large amounts of raw text. They work well, if you have a text at least a few sentences long you can usually make enough educated guesses.

But it can be improved.

Current tables have the probabilities of "e" being the first letter of a word is the same as for the third letter. That's not true in practice. This research is to create new letter frequency tables based off of letter positions and word length.

## The Process

The first step was deciding on where I would get the words that I would be measuring. There are a few schools of thought on what data should be used to find the most accurate ratios of letter frequencies.

### Dictionary

The easiest data to gather is just using a dictionary, with one appearance of every word in the language that you're measuring (english for me). This will get rather accurate frequencies, but the problem with this method is that not all words are used the same amount of times. If you have a dictionary like so

```
the
axe
ran
fix
```

the letter 'e' will appear about 16% of the time. This is pretty close to what traditional letter frequencies have the letter at. But the problem is, words like 'the' appear much more often in most texts than words like 'ran', so any text you actually try to break will have the letters 'the' appear more often then the letters 'fix'. So we know that we have to account for frequency of words appearing in a text in addition to the frequency of letters in a word, but how do we do that?

### The Written Word

The next step is to analyze the frequencies of words in a real text. So where do we find large amounts of easily readable (and legally usable) text? The standard answer is usually a.) **Books from project Gutenberg** and b.) **Wikipedia**. Both are good answers, they provide large, usable, human-generated text corpora (corpuses?) which are easy to parse and free to use. This is the approach that most letter frequency tables (and many other projects) use. But there's one problem for us. We are trying to break messages written somewhat recently by a human. Most people nowdays don't talk like

```
But look! here come more crowds, pacing straight for the water, and seemingly bound for a dive. Strange! Nothing will content them but the extremest limit of the land; loitering under the shady lee of yonder warehouses will not suffice. No. They must get just as nigh the water as they possibly can without falling in. And there they stand—miles of them—leagues. Inlanders all, they come from lanes and alleys, streets and avenues—north, east, south, and west. Yet here they all unite. Tell me, does the magnetic virtue of the needles of the compasses of all those ships attract them thither?
```
(From Moby Dick on Project Gutenberg)

or 

```
   TITANIA. Then I must be thy lady; but I know
    When thou hast stolen away from fairy land,
    And in the shape of Corin sat all day,
    Playing on pipes of corn, and versing love
    To amorous Phillida. Why art thou here,
    Come from the farthest steep of India,
    But that, forsooth, the bouncing Amazon,
    Your buskin'd mistress and your warrior love,
    To Theseus must be wedded, and you come
    To give their bed joy and prosperity?
```
(From A Midsummer's Night Dream on Project Gutenberg)

or

```
A Riemann surface X is a topological space that is locally homeomorphic to an open subset of C, the set of complex numbers. In addition, the transition maps between these open subsets are required to be holomorphic. The latter condition allows one to transfer the notions and methods of complex analysis dealing with holomorphic and meromorphic functions on C to the surface X. For the purposes of the Riemann–Roch theorem, the surface X is always assumed to be compact. Colloquially speaking, the genus g of a Riemann surface is its number of handles; for example the genus of the Riemann surface shown at the right is three. More precisely, the genus is defined as half of the first Betti number, i.e., half of the C-dimension of the first singular homology group H 1 ( X , C ) with complex coefficients. The genus classifies compact Riemann surfaces up to homeomorphism, i.e., two such surfaces are homeomorphic if and only if their genus is the same. Therefore, the genus is an important topological invariant of a Riemann surface. On the other hand, Hodge theory shows that the genus coincides with the C-dimension of the space of holomorphic one-forms on X, so the genus also encodes complex-analytic information about the Riemann surface.
```
(From the Riemann–Roch theorem on Wikipedia)

These are obviously handpicked to make a point, but the problem still remains. The texts from Project Gutenberg are most often in the public domain because they were written at least 95 years ago, and the text from Wikipedia is (by design) written like an encyclopedia. That means that the text is often too technical or written in a style of English that isn't used today. You will be hard pressed to find instances of today's conversational english in either of the corpora.

That takes us to the last option.

### The (Modern) Written Word

The text that we are trying to break is likely modern conversational english, so it stands to reason that in order to find the most effective frequencies to break our ciphertext, we should analyze a dataset of modern conversational english. I used the [Cornell Movie-Dialogs Corpus](https://convokit.cornell.edu/documentation/movie.html), it has 220,579 conversations from 617 movie scripts. I wrote a quick script which filtered out formatting stuff, punctuation, speakers' names, and numbers, and writes all of the words to a new .txt file. But wait. Doesn't using a dataset which is based off of movie dialogue mean that we end up with fictitious words like "borg"? Yes, but thankfully we have a list of every real word in the english language. So after writing a quick script which filters out words from the Cornell Corpus which aren't in the dictionary, we end up with a nice list of real words used in thousands of conversations.

Now we feed the new list through our fancy letter frequency calculator and get a new set of letter frequencies. 

## Results

You can find my results in my [Github Repo](https://github.com/ThisIsNotANamepng/LetterFrequencyData)