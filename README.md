# Citer

A citation generator tool for Wikipedia. Currently accessible from:\
http://citer.toolforge.org/ (the English version)\
http://yadfa.toolforge.org/ (the Persian version)

## What does it do?

Citer is especially useful for generating citations from Google Books URLs, DOIs (Any Digital object Identifiers) and ISBNs (International Standard Book Numbers).
Additionally, URLs of many major news websites are supported, including:

* The New York Times
* BBC
* Daily Mail
* Daily Mirror
* The Daily Telegraph
* The Huffington Post
* The Washington Post
* The Boston Globe
* Bloomberg Businessweek
* Financial Times
* The Times of India

Special support for the URLs of the [Wayback Machine](https://en.wikipedia.org/wiki/Wayback_Machine) is also implemented.

Some other tested and supported Persian web-sites:
* http://www.noormags.ir (نورمگز)
* http://www.noorlib.ir (کتابخانه دیجیتال نور)
* http://www.ketab.ir (خانه كتاب)
* http://socialhistory.ihcs.ac.ir/ (تحقیقات تاریخ اجتماعی)


## Installation

To run Citer on your local computer:

1. Install Python 3.7+.
2. Clone the project.
3. Install the dependencies using `pip install -r requirements.txt`.
3. Make sure that `flup` is __not__ installed in your environment.
5. Copy `config.py.example` to `config.py`. (You might want to get an NCBI API key and add it to the config file if you're going to use its services.)
4. Run `python3 app.py`.

If everything goes fine, the main page will be accessible from:\
    http://localhost:5000/

## Language Setting
The default language is English and can be changed to Persian using the setting in the config.py file.
