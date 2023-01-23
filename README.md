# ENcycloPYdia (ENPY): 📗🥷
### The English Language JSON 

---
## So, what's going on here?

Sleep deprivation*, mostly, but allow me to explain in a hopefully TL;DR format: I'm building a different app that requires free, unlimited access to the english language on the fly. This app is supposed to help people study, and I'm calling it _RabbitHole_ (I'll link you guys once there's some more headway). In this app, I need to run 500 definition searches at the same time to reflect a users' relevancy during their studies. Web scraping to accomplish this task is... well, unrealistic, unless everyone is going to willingly solve captchas all the time. Or unless I incorporate rotating proxies in each program and web scrape for available IPs constantly (thanks Adam--see footnote). Either way, I think it's more efficient to just create a JSON. Perhaps this will land in a DB, or maybe I'll just keep the full JSON with the program for now and figure out a GH Actions pipeline to keep it current. 

---
## Why not just X, Y, or Z instead of stealing the English Language? 

Because it hasn't been done before, go ahead and do your Google search. We have a few candidates that rub close, but nothing as extensive as ENPY has ever been built. I'm the first human to do it, and I'm proud to contribute to the future of humanity, no matter how small. 

I hope this benefits you, I'd appreciate a shoutout or mention if it does! I do realize most will likely steal the JSON and never give credit where due. That's ok too, it's the thought that counts.

---
## The future of ENPY? 

In my dreams, ENPY gets contributed to by others. A CLI or some kind of GUI is built to allow people to insert new entries and modify existing ones. A rotating proxy is incorporated, and we successfully web scrape every possible English word source on the internet for dictionary entries from the start of humanity, to the present of humanity. One day, someone in a Spanish speaking country thinks it's cool, and we get ESPY. Then FRPY, and ITPY, and BoisenBerryPY, and PumpkinPY... 

*: It's 4am and my daughter has woken me up, I don't even have any pie and I'm probably not going to eat for a while, but this would be a good spot for a shameless donation link so that you could buy me a coffee and I could write better readme's.

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/Fiattarone)

---
## Features 

Here's the format of the JSON in its current state:

```
{
    "words": [
        {
            "word": "",
            definition: "" || {
                "number": "def",
                ...
            },
            synonyms: "" || {
                "number": "syn",
                ...
            },
            antonyms: "" || {
                "number": "ant",
                ...
            },
        },...
    ],
    "stats": etc
}
```

I have the stats in a separate JSON file currently. They'll merge. Just give them time to warm up to each other. 

---
## TODO

1) Rotating proxy incorporation for future scrapes 
2) Moar words and therefore moar sauces
3) Add word feat.
4) Refactor
5) CLI Client
6) ????
7) Profit! 

---
## THE DB 

Experimenting with uploading the json to a DB for all to access. If I start incurring fees from this then we're going to
Elon-up and make a subscription model. 🤪

Here's the codes for future reference. 

```
mongoimport --uri "mongodb+srv://enpy:test123@cluster.mongodb.net/ENPY" --collection ENPY --file /Users/dfiatt/Documents/web_development/ENcycloPYdia/ENcycloPYdia_hashed.json
```

---
## Le Memes:

![NickCage](memes/NickCage.jpg)

![Bilbo](memes/Bilbo.jpg)

![PerfectStorm](memes/PerfectStorm.jpg)

---
## THANKS

These are the kind humans I have to thank for this project: 

#### [Jbusma](https://github.com/Jbusma) -- Who else would have the mental caliber to come up with such a genius name? Go shoot this guy a DM and take a look at how he's about to change the Real Estate game.
#### [dwyl](https://github.com/dwyl) -- dwyl, man, I stole your [word list](https://github.com/dwyl/english-words)! (Meme to commemorate this coming soon)
#### [Adam Fisher](https://linkedin.com/in/adamfisher4) -- Plain and simple, another genius with incredible insight. Out of 2.3k people that viewed my cry for help on LinkedIn, this guy was the one talented soul to come in clutch. Wish I had his GH to promote. 