tags:Cybersecurity, Cryptography
date:2025-01-02
# Wacky Hardware Randomness Methods

If you're familiar with modern cryptography you know that you need randomness to securely encrypt data. If you know that then you probably know of Cloudflare's [San Francisco headquarters lava lamp wall](https://blog.cloudflare.com/randomness-101-lavarand-in-production) (LavaRand for short). That got me thinking, if you can get cryptographically secure randomness from a lava lamp, what else could you get randomness from? 

## Methodology

I took 10 second videos of various stimuli and read the bits with a quick python line:

    with open(file_path, 'rb') as file:
            bytes = file.read()

and measured the entropy with a quick python function (are you sensing a pattern here?):

    def calculate_entropy(data):
        # Count the frequency of each byte value
        byte_counts = Counter(data)
        total_bytes = len(data)
        
        # Calculate the entropy
        entropy = -sum((count / total_bytes) * log2(count / total_bytes) for count in byte_counts.values())
        return entropy

For standardization sake, I removed the sound of all of the video I took.

I know that this is in no way a complete, accurate way to approach the nuanced problem of true randomness, but it probably works for my reasons. 

### Lava Lamp

How better to start than the original? 

    entropy: 6.249883274606861

[Lava lamp video](/static/randomness/lavalamp.mp4)

### Fish Tank

If the saying is true, the fish shouldn't be able to remember enough to make patterns and be predictable (I know there aren't goldfish in the tank but still)

This video is from my friend. All of the incredible fame, recognition, and profit I make from this portion of this article belongs to them.

    entropy: 7.999765468210011

[Fish tank video](/static/randomness/fish.mp4)

### Campfire

In addition to the whole "fireness" of the fire, I suppose the placement of the logs would theoretically add to the randomness. I wanted to get a video, but I was too lazy to build a proper fire.

### Sprinkler

Inspired by this [https://mast.hpc.social/@stux@mstdn.social/112436286233259933](https://mast.hpc.social/@stux@mstdn.social/112436286233259933). I put my phone in a bag, and sprayed it with a hose. My ability to elevate the tech I'm working with is obviously the reason I'm so sought after for my research abilities. 

    entropy: 7.999989992286659

[Sprinkler video](/static/randomness/sprinkler.mp4)

I also measured the entropy of of the version of the video I took with sound, because it really adds a lot to the whole experience. I thought it would add randomness, but it actually has slightly less entropy than the silent version. I blame this on my entropy measuring methods.

    entropy: 7.999976279852674

[Sprinkler with sound video](/static/randomness/sprinkler_sound.mp4)

### Duck Cam Livestream

There is a [fish doorbell](https://www.nytimes.com/2024/03/28/style/fish-doorbell-visdeurbel-netherlands.html) that I wanted to use but alas, as of this writing its not in season. Luckily, there's a river flowing through my college campus which is a frequent highway for ducks. [https://www.uwec.edu/learning-technology-services/live-streaming/uw-eau-claire-duck-cam/](https://www.uwec.edu/learning-technology-services/live-streaming/uw-eau-claire-duck-cam/)

Obviously, I didn't take this video, it belongs to [UW Eau Claire](https://uwec.edu).

    entropy: 7.96928220287236

[Duck livestream video](/static/randomness/ducklivestream.mp4)

### Footbridge Livestream

The duck livestream led me to a livestream of UWEC's footbridge over the Chippewa River. In addition to the river, trees, and wildlife that the duck cam has, it also has a frequent view of students crossing the bridge, adding additional randomness (even though there aren't many students in in the video I recorded because it was summer when I wrote this). [https://www.uwec.edu/learning-technology-services/live-streaming/footbridge-live-stream/](https://www.uwec.edu/learning-technology-services/live-streaming/footbridge-live-stream/)

This video also belongs to [UW Eau Claire](https://uwec.edu).

[Footbridge livestream video](/static/randomness/ducklivestream.mp4)

### Times Square Livestream

The lack of students in the footbridge livestream made me sad, but then I wondered if there was another livestream which did have people (in a non identifying way, of course). Luckily, New York exists. There are a number of livestreams of downtown New York perpetually filled with tourists randomly meandering the streets. I could not think of a better way to capture true randomness than by analyzing the confusion of tourists. Again, I obviously did not record this video, all credit goes to [EarthCam](https://www.earthcam.com), I got the video from [https://www.earthcam.com/usa/newyork/timessquare/?cam=tsrobo1](https://www.earthcam.com/usa/newyork/timessquare/?cam=tsrobo1).

    entropy: 7.986465972907881

[Times Square livestream video](/static/randomness/timessquarelivestream.mp4)

## Results

All in all, the silent sprinkler was the most random of the methods I measured at 7.999989992286659. I compared this to the randomness I could generate with python.

    def generate_random_bytes(length):
        return bytes(random.getrandbits(8) for _ in range(length))

    def generate_secure_random_bytes(length):
        return secrets.token_bytes(length)

With plain [`random`](https://docs.python.org/3/library/random.html) the "randomly" generated bytes (with a length of the amount of bytes in the lavalamp video) had an entropy of 7.999834961004065

The bytes generated by the [`secrets`](https://docs.python.org/3/library/secrets.html) module (which uses /dev/urandom as a backend) had an entropy of 7.999838620600613. Just slightly better than the non-cryptographically secure generated bytes.

If I didn't know that my method of measuring randomness was flawed before, the fact that the video of me spraying my phone with a hose measured more random than the bytes generated by the module written by thousands of incredibly intelligent developers of the Linux kernel really brings it home.